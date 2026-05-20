"""Gemini Batch API integration for the experiment.

Submits, polls, and parses inline batch jobs. State (batch resource names) is
owned by `experiments.state`; this module is stateless apart from the
`genai.Client` it wraps.

Provider note: Google's Batch API runs asynchronously server-side with an SLA
of up to 24 hours (typically <1 hour). The client side just submits, records
the resource name, and polls — interruptions on the client are safe because
the batch keeps running on Google's infrastructure and can be re-fetched by
its resource name on the next CLI invocation.
"""

from __future__ import annotations

import logging
import time

from google import genai
from google.genai import types

from experiments.config import (
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    POLL_INTERVAL_SECONDS,
    POLL_TIMEOUT_HOURS,
    get_api_key,
)

logger = logging.getLogger(__name__)


_TERMINAL_STATES = {"JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED", "JOB_STATE_CANCELLED"}


def get_client() -> genai.Client:
    return genai.Client(api_key=get_api_key())


def build_inline_request(prompt: str, run_id: str) -> types.InlinedRequest:
    """Wrap one prompt as a Gemini batch inline request, tagged with run_id."""
    return types.InlinedRequest(
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
        config=types.GenerateContentConfig(
            temperature=GEMINI_TEMPERATURE,
            max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
        ),
        metadata={"run_id": run_id},
    )


def submit_batch(
    client: genai.Client,
    inline_requests: list[types.InlinedRequest],
    display_name: str,
) -> str:
    """Submit a batch and return its resource name (e.g. 'batches/abc123')."""
    if not inline_requests:
        raise ValueError("submit_batch called with empty inline_requests")
    job = client.batches.create(
        model=GEMINI_MODEL,
        src=inline_requests,
        config=types.CreateBatchJobConfig(display_name=display_name),
    )
    logger.info(
        "Submitted batch %s with %d requests (state=%s)",
        job.name,
        len(inline_requests),
        getattr(job.state, "name", str(job.state)),
    )
    return job.name


def poll_batch(client: genai.Client, batch_name: str) -> types.BatchJob:
    """Poll until terminal state, then return the BatchJob.

    Safe to interrupt — re-running just re-fetches by name and resumes polling.
    """
    deadline = time.monotonic() + POLL_TIMEOUT_HOURS * 3600
    while True:
        job = client.batches.get(name=batch_name)
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


def fetch_results(job: types.BatchJob) -> list[dict]:
    """Parse the inline responses of a completed BatchJob into raw dicts.

    Each row contains: run_id (from metadata), text (raw LLM output), tokens_in,
    tokens_out, cached_tokens (0 — no caching enabled yet), error.
    """
    state_name = getattr(job.state, "name", str(job.state))
    if state_name != "JOB_STATE_SUCCEEDED":
        raise RuntimeError(
            f"Batch {job.name} is in non-success state: {state_name}; "
            f"error={getattr(job, 'error', None)}"
        )

    dest = job.dest
    if dest is None or dest.inlined_responses is None:
        raise RuntimeError(
            f"Batch {job.name} succeeded but has no inlined_responses — was it "
            f"submitted with an inline source?"
        )

    rows: list[dict] = []
    for inline in dest.inlined_responses:
        run_id = (inline.metadata or {}).get("run_id")
        if inline.error is not None:
            rows.append(
                {
                    "run_id": run_id,
                    "text": "",
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "cached_tokens": 0,
                    "error": str(inline.error),
                }
            )
            continue

        resp = inline.response
        text = ""
        if resp is not None:
            text = getattr(resp, "text", "") or ""
            if not text and resp.candidates:
                # Fallback: stitch parts manually if .text isn't populated.
                for cand in resp.candidates:
                    content = getattr(cand, "content", None)
                    if content and content.parts:
                        for part in content.parts:
                            if getattr(part, "text", None):
                                text += part.text
        usage = getattr(resp, "usage_metadata", None) if resp is not None else None
        rows.append(
            {
                "run_id": run_id,
                "text": text,
                "tokens_in": getattr(usage, "prompt_token_count", 0) or 0,
                "tokens_out": getattr(usage, "candidates_token_count", 0) or 0,
                "cached_tokens": getattr(usage, "cached_content_token_count", 0) or 0,
                "error": None,
            }
        )
    logger.info("Fetched %d responses from %s", len(rows), job.name)
    return rows
