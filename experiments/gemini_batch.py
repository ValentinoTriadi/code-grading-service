"""Gemini Batch integration for the experiment — AI Studio + Vertex AI.

Submits, polls, and parses batch jobs against either backend. State (batch
resource names) is owned by `experiments.state`; this module is stateless
apart from the `genai.Client` it wraps and the `storage.Client` it
optionally uses for Vertex.

Backend selection is driven by `EXPERIMENT_USE_VERTEX` (see
`experiments/config.py`). The two paths differ materially:

- **AI Studio** (default): inline batch — requests live inside the API call
  as `InlinedRequest` objects, responses come back inline. No GCS needed.
- **Vertex AI**: JSONL batch — requests are uploaded to GCS, the batch job
  reads from `gs://.../input.jsonl` and writes to `gs://.../output/`, and
  results are streamed back from GCS once the job succeeds. Run-IDs are
  preserved via a sidecar JSON file (Vertex Batch has no per-row metadata
  field equivalent to AI Studio's `InlinedRequest.metadata`).

Provider note: Google's Batch API runs asynchronously server-side with an
SLA of up to 24 hours (typically <1 hour). The client side just submits,
records the resource name, and polls — interruptions on the client are
safe because the batch keeps running on Google's infrastructure and can
be re-fetched by its resource name on the next CLI invocation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any

import httpx
from google import genai
from google.api_core import exceptions as gax_exceptions
from google.cloud import storage
from google.genai import types

from experiments.config import (
    GCP_LOCATION,
    GCP_PROJECT,
    GCS_BUCKET,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    POLL_INTERVAL_SECONDS,
    POLL_TIMEOUT_HOURS,
    USE_VERTEX,
    assert_vertex_config,
    get_api_key,
)

logger = logging.getLogger(__name__)


_TERMINAL_STATES = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED"}

# Network/server errors that should NOT abort a 24h poll loop. The genai SDK
# adds its own retries on top of httpx, but doesn't catch RemoteProtocolError
# and a handful of API-core 5xx exceptions, which surface as fatal during long
# polls (especially over flaky links). We absorb them and keep polling.
_TRANSIENT_POLL_ERRORS: tuple[type[Exception], ...] = (
    httpx.RemoteProtocolError,
    httpx.ReadError,
    httpx.WriteError,
    httpx.ConnectError,
    httpx.ReadTimeout,
    httpx.ConnectTimeout,
    httpx.PoolTimeout,
    gax_exceptions.ServiceUnavailable,
    gax_exceptions.InternalServerError,
    gax_exceptions.GatewayTimeout,
    gax_exceptions.DeadlineExceeded,
)

# Maximum consecutive transient failures before we give up on a poll loop.
# At the default 60s poll interval, 30 failures ≈ 30 min of full outage.
_MAX_TRANSIENT_POLL_FAILURES = 30


@dataclass(frozen=True)
class BatchRequest:
    """Provider-agnostic request representation.

    Holds the rendered prompt plus the run_id that the runner uses to match
    responses back to cells. Both backends materialise this into their own
    on-the-wire format inside `submit_batch`.
    """

    prompt: str
    run_id: str


# --- client construction ---------------------------------------------------


def get_client() -> genai.Client:
    """Build a Gemini client for the configured backend.

    Vertex mode uses Application Default Credentials — run
    `gcloud auth application-default login` once locally. AI Studio mode
    uses the `GEMINI_API_KEY` env var.
    """
    if USE_VERTEX:
        assert_vertex_config()
        logger.info(
            "Gemini client mode=Vertex project=%s location=%s",
            GCP_PROJECT,
            GCP_LOCATION,
        )
        return genai.Client(
            vertexai=True, project=GCP_PROJECT, location=GCP_LOCATION
        )
    logger.info("Gemini client mode=AI-Studio (API key)")
    return genai.Client(api_key=get_api_key())


def build_inline_request(prompt: str, run_id: str) -> BatchRequest:
    """Provider-agnostic request builder.

    The name is kept for runner compatibility — historically this returned
    a `types.InlinedRequest`, but the AI-Studio-specific construction now
    happens inside `_submit_batch_aistudio` so the runner stays unaware of
    which backend is active.
    """
    return BatchRequest(prompt=prompt, run_id=run_id)


# --- batch submission ------------------------------------------------------


def submit_batch(
    client: genai.Client,
    requests: list[BatchRequest],
    display_name: str,
) -> str:
    """Submit a batch and return its resource name.

    `display_name` is reused as the GCS sub-prefix on Vertex so input/output
    blobs are namespaced per batch (e.g. `phase1-S5/input.jsonl`).
    """
    if not requests:
        raise ValueError("submit_batch called with empty requests")
    if USE_VERTEX:
        return _submit_batch_vertex(client, requests, display_name)
    return _submit_batch_aistudio(client, requests, display_name)


def _submit_batch_aistudio(
    client: genai.Client,
    requests: list[BatchRequest],
    display_name: str,
) -> str:
    inline = [
        types.InlinedRequest(
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=r.prompt)])
            ],
            config=types.GenerateContentConfig(
                temperature=GEMINI_TEMPERATURE,
                max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
            ),
            metadata={"run_id": r.run_id},
        )
        for r in requests
    ]
    job = client.batches.create(
        model=GEMINI_MODEL,
        src=inline,
        config=types.CreateBatchJobConfig(display_name=display_name),
    )
    logger.info(
        "Submitted AI-Studio batch %s with %d requests (state=%s)",
        job.name,
        len(inline),
        getattr(job.state, "name", str(job.state)),
    )
    return job.name


def _prompt_hash(prompt: str) -> str:
    """Stable short hash used to match Vertex output rows back to run_ids.

    Vertex Batch does NOT guarantee output row order matches input row
    order — rows are processed in parallel and emitted as they finish. We
    therefore identify each output row by hashing its request prompt and
    looking the hash up in a sidecar uploaded at submit time. Truncating
    to 16 hex chars (64 bits) is more than enough to disambiguate within
    a single batch.
    """
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def _submit_batch_vertex(
    client: genai.Client,
    requests: list[BatchRequest],
    display_name: str,
) -> str:
    bucket_name, prefix = _parse_bucket_uri(GCS_BUCKET)
    base = _join_prefix(prefix, display_name)

    jsonl_body = "\n".join(
        json.dumps(
            {
                "request": {
                    "contents": [
                        {"role": "user", "parts": [{"text": r.prompt}]}
                    ],
                    "generation_config": {
                        "temperature": GEMINI_TEMPERATURE,
                        "max_output_tokens": GEMINI_MAX_OUTPUT_TOKENS,
                    },
                }
            }
        )
        for r in requests
    )
    # Multi-valued because Phase 2 submits 7 replicates of identical prompts.
    # Same prompt → same hash → multiple run_ids; we pop them in submit order
    # when matching output rows back.
    hash_to_run_ids: dict[str, list[str]] = defaultdict(list)
    for r in requests:
        hash_to_run_ids[_prompt_hash(r.prompt)].append(r.run_id)

    storage_client = storage.Client(project=GCP_PROJECT)
    bucket = storage_client.bucket(bucket_name)

    input_blob = f"{base}/input.jsonl"
    sidecar_blob = f"{base}/run_ids.json"
    bucket.blob(input_blob).upload_from_string(
        jsonl_body, content_type="application/jsonl"
    )
    bucket.blob(sidecar_blob).upload_from_string(
        json.dumps(dict(hash_to_run_ids)), content_type="application/json"
    )

    input_uri = f"gs://{bucket_name}/{input_blob}"
    output_uri = f"gs://{bucket_name}/{base}/output/"

    job = client.batches.create(
        model=GEMINI_MODEL,
        src=input_uri,
        config=types.CreateBatchJobConfig(
            display_name=display_name,
            dest=output_uri,
        ),
    )
    logger.info(
        "Submitted Vertex batch %s — input=%s output=%s requests=%d",
        job.name,
        input_uri,
        output_uri,
        len(requests),
    )
    return job.name


# --- polling ---------------------------------------------------------------


def poll_batch(client: genai.Client, batch_name: str) -> types.BatchJob:
    """Poll until terminal state, then return the BatchJob.

    Safe to interrupt — re-running just re-fetches by name and resumes
    polling. Identical behaviour on AI Studio and Vertex; the `BatchJob`
    abstraction normalises both backends.

    Transient network or 5xx errors during `batches.get` are absorbed and
    the loop continues — long batches over flaky connections shouldn't
    crash the runner; the batch itself keeps running server-side.
    """
    deadline = time.monotonic() + POLL_TIMEOUT_HOURS * 3600
    transient_failures = 0
    while True:
        try:
            job = client.batches.get(name=batch_name)
        except _TRANSIENT_POLL_ERRORS as exc:
            transient_failures += 1
            logger.warning(
                "Batch %s transient poll error (%d/%d): %s",
                batch_name,
                transient_failures,
                _MAX_TRANSIENT_POLL_FAILURES,
                exc,
            )
            if transient_failures >= _MAX_TRANSIENT_POLL_FAILURES:
                raise
            time.sleep(POLL_INTERVAL_SECONDS)
            continue
        transient_failures = 0
        state_name = getattr(job.state, "name", str(job.state))
        logger.info("Batch %s state=%s", batch_name, state_name)
        if state_name in _TERMINAL_STATES:
            return job
        if time.monotonic() > deadline:
            raise TimeoutError(
                f"Batch {batch_name} did not reach a terminal state within "
                f"{POLL_TIMEOUT_HOURS}h (last state: {state_name})"
            )
        time.sleep(POLL_INTERVAL_SECONDS)


# --- result fetching -------------------------------------------------------


def fetch_results(job: types.BatchJob) -> list[dict]:
    """Parse a completed BatchJob's responses into raw dicts.

    Each row contains: run_id, text, tokens_in, tokens_out, cached_tokens,
    error. The runner zips these onto Cell objects by `run_id`.
    """
    state_name = getattr(job.state, "name", str(job.state))
    if state_name != "JOB_STATE_SUCCEEDED":
        raise RuntimeError(
            f"Batch {job.name} is in non-success state: {state_name}; "
            f"error={getattr(job, 'error', None)}"
        )
    if USE_VERTEX:
        return _fetch_results_vertex(job)
    return _fetch_results_aistudio(job)


def _fetch_results_aistudio(job: types.BatchJob) -> list[dict]:
    dest = job.dest
    if dest is None or dest.inlined_responses is None:
        raise RuntimeError(
            f"Batch {job.name} succeeded but has no inlined_responses — was it "
            f"submitted with an inline source? (AI Studio mode expected.)"
        )

    rows: list[dict] = []
    for inline in dest.inlined_responses:
        run_id = (inline.metadata or {}).get("run_id")
        if inline.error is not None:
            rows.append(_error_row(run_id, str(inline.error)))
            continue
        rows.append(_row_from_response(run_id, inline.response))
    logger.info("Fetched %d responses from %s (AI Studio)", len(rows), job.name)
    return rows


def _fetch_results_vertex(job: types.BatchJob) -> list[dict]:
    """Stream the Vertex Batch output JSONL back from GCS and align run_ids.

    Vertex Batch processes requests in parallel and does NOT guarantee
    output row order matches input row order. Each output row carries its
    own `request` payload (containing the prompt), so we match outputs to
    run_ids by hashing each output's prompt and looking it up in the
    sidecar uploaded at submit time. Duplicate-prompt cases (Phase 2's 7
    replicates of identical prompts) are handled by popping run_ids from
    the per-hash queue in submit order.

    The output is written under `dest/predictions-*.jsonl` (one or more
    shard files); we concatenate them in lexicographic order.
    """
    input_uri = _vertex_input_uri(job)
    output_prefix_uri = _vertex_output_prefix_uri(job)
    bucket_name, input_blob = _parse_gcs_uri(input_uri)
    _, output_prefix = _parse_gcs_uri(output_prefix_uri)
    base = input_blob.rsplit("/", 1)[0]  # strip /input.jsonl
    sidecar_blob = f"{base}/run_ids.json"

    storage_client = storage.Client(project=GCP_PROJECT)
    bucket = storage_client.bucket(bucket_name)

    hash_to_run_ids_raw: dict[str, list[str]] = json.loads(
        bucket.blob(sidecar_blob).download_as_text()
    )
    # Convert to mutable deques so we can pop in submit order for duplicates.
    pending: dict[str, deque[str]] = {
        h: deque(ids) for h, ids in hash_to_run_ids_raw.items()
    }
    total_expected = sum(len(ids) for ids in hash_to_run_ids_raw.values())

    shards = sorted(
        bucket.list_blobs(prefix=output_prefix.rstrip("/")),
        key=lambda b: b.name,
    )
    shards = [b for b in shards if b.name.endswith(".jsonl")]
    if not shards:
        raise RuntimeError(
            f"Batch {job.name} succeeded but no JSONL output shards found "
            f"under gs://{bucket_name}/{output_prefix}"
        )

    output_lines: list[str] = []
    for shard in shards:
        text = shard.download_as_text()
        output_lines.extend(line for line in text.splitlines() if line.strip())

    if len(output_lines) != total_expected:
        logger.warning(
            "Batch %s output row count (%d) != input row count (%d). "
            "Will still attempt prompt-hash matching.",
            job.name,
            len(output_lines),
            total_expected,
        )

    rows: list[dict] = []
    for line in output_lines:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            rows.append(_error_row(None, f"output_parse_error: {exc!r}"))
            continue

        prompt = _extract_request_prompt(obj.get("request") or {})
        run_id = _pop_run_id(pending, prompt)

        status = obj.get("status") or ""
        if status and status != "":
            rows.append(_error_row(run_id, f"vertex_status: {status}"))
            continue
        response = obj.get("response")
        if response is None:
            rows.append(_error_row(run_id, "no_response_in_output_row"))
            continue
        rows.append(_row_from_vertex_response(run_id, response))

    unmatched = sum(len(q) for q in pending.values())
    if unmatched:
        logger.warning(
            "Batch %s has %d unmatched run_id(s) after fetching — output "
            "may be incomplete.",
            job.name,
            unmatched,
        )
    logger.info("Fetched %d responses from %s (Vertex)", len(rows), job.name)
    return rows


def _extract_request_prompt(request: dict) -> str:
    """Pull the user prompt text out of a Vertex Batch request payload.

    Output rows include the original `request` dict so we can recover the
    prompt and hash it for matching. Returns empty string if the structure
    is unexpected — the caller will treat that as an unmatched row.
    """
    contents = request.get("contents") or []
    if not contents:
        return ""
    parts = contents[0].get("parts") or []
    if not parts:
        return ""
    return parts[0].get("text") or ""


def _pop_run_id(pending: dict[str, deque[str]], prompt: str) -> str | None:
    """Look up the next run_id for this prompt and remove it from the queue."""
    h = _prompt_hash(prompt)
    q = pending.get(h)
    if not q:
        return None
    return q.popleft()


# --- response row helpers --------------------------------------------------


def _row_from_response(run_id: str | None, resp: Any) -> dict:
    """Build a result row from a `GenerateContentResponse`-shaped object."""
    text = ""
    if resp is not None:
        text = getattr(resp, "text", "") or ""
        if not text and getattr(resp, "candidates", None):
            for cand in resp.candidates:
                content = getattr(cand, "content", None)
                if content and content.parts:
                    for part in content.parts:
                        if getattr(part, "text", None):
                            text += part.text
    usage = getattr(resp, "usage_metadata", None) if resp is not None else None
    return {
        "run_id": run_id,
        "text": text,
        "tokens_in": getattr(usage, "prompt_token_count", 0) or 0,
        "tokens_out": getattr(usage, "candidates_token_count", 0) or 0,
        "cached_tokens": getattr(usage, "cached_content_token_count", 0) or 0,
        "error": None,
    }


def _row_from_vertex_response(run_id: str, response: dict) -> dict:
    """Build a result row from a Vertex Batch output `response` dict.

    Vertex returns the raw `GenerateContentResponse` JSON, which uses
    camelCase keys (`usageMetadata.promptTokenCount`) rather than the
    snake_case attrs the Python SDK exposes on inline responses.
    """
    text = ""
    candidates = response.get("candidates") or []
    for cand in candidates:
        content = cand.get("content") or {}
        for part in content.get("parts") or []:
            t = part.get("text")
            if t:
                text += t
    usage = response.get("usageMetadata") or {}
    return {
        "run_id": run_id,
        "text": text,
        "tokens_in": usage.get("promptTokenCount", 0) or 0,
        "tokens_out": usage.get("candidatesTokenCount", 0) or 0,
        "cached_tokens": usage.get("cachedContentTokenCount", 0) or 0,
        "error": None,
    }


def _error_row(run_id: str | None, msg: str) -> dict:
    return {
        "run_id": run_id,
        "text": "",
        "tokens_in": 0,
        "tokens_out": 0,
        "cached_tokens": 0,
        "error": msg,
    }


# --- GCS URI helpers -------------------------------------------------------


def _parse_bucket_uri(uri: str) -> tuple[str, str]:
    """Split `gs://bucket/prefix/...` or `bucket/prefix/...` into (bucket, prefix)."""
    if uri.startswith("gs://"):
        uri = uri[len("gs://") :]
    parts = uri.split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) == 2 else ""
    return bucket, prefix.strip("/")


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    """Split a fully-qualified `gs://bucket/path/to/blob` into (bucket, blob)."""
    if not uri.startswith("gs://"):
        raise ValueError(f"Expected gs:// URI, got: {uri}")
    rest = uri[len("gs://") :]
    bucket, _, blob = rest.partition("/")
    return bucket, blob


def _join_prefix(prefix: str, suffix: str) -> str:
    if not prefix:
        return suffix
    return f"{prefix.rstrip('/')}/{suffix}"


def _vertex_input_uri(job: types.BatchJob) -> str:
    """Recover the input GCS URI from a Vertex BatchJob."""
    src = getattr(job, "src", None)
    if src is None:
        raise RuntimeError(f"Batch {job.name} has no .src — cannot locate input.")
    gcs = getattr(src, "gcs_uri", None)
    if isinstance(gcs, list):
        if not gcs:
            raise RuntimeError(f"Batch {job.name} src.gcs_uri is an empty list.")
        return gcs[0]
    if isinstance(gcs, str) and gcs:
        return gcs
    raise RuntimeError(
        f"Batch {job.name} has no GCS input URI on .src (got {src!r}). "
        f"Vertex batch expected."
    )


def _vertex_output_prefix_uri(job: types.BatchJob) -> str:
    """Recover the output GCS prefix URI from a Vertex BatchJob."""
    dest = getattr(job, "dest", None)
    if dest is None:
        raise RuntimeError(f"Batch {job.name} has no .dest — cannot locate output.")
    gcs = getattr(dest, "gcs_uri", None)
    if isinstance(gcs, str) and gcs:
        return gcs
    raise RuntimeError(
        f"Batch {job.name} has no GCS output URI on .dest (got {dest!r}). "
        f"Vertex batch expected."
    )
