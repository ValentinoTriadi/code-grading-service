"""Configuration for the experiment runner.

All knobs are tunable via env vars so a re-run can change one parameter without
touching code. Defaults match docs/design/experiment-plan.md.
"""

from __future__ import annotations

import os
from pathlib import Path

EXPERIMENTS_DIR = Path(__file__).parent
DATASET_DIR = EXPERIMENTS_DIR / "dataset"
RESULTS_DIR = EXPERIMENTS_DIR / "results"
STATE_FILE = EXPERIMENTS_DIR / "state.json"
PHASE1_RESULTS = RESULTS_DIR / "phase1.jsonl"
PHASE2_RESULTS = RESULTS_DIR / "phase2.jsonl"

GEMINI_MODEL = os.environ.get("EXPERIMENT_MODEL", "gemini-2.5-flash")
GEMINI_TEMPERATURE = float(os.environ.get("EXPERIMENT_TEMPERATURE", "0.5"))
GEMINI_MAX_OUTPUT_TOKENS = int(os.environ.get("EXPERIMENT_MAX_OUTPUT_TOKENS", "2500"))
# Optional override for CoT-heavy scenarios that need more output space.
GEMINI_MAX_OUTPUT_TOKENS_COT = int(
    os.environ.get("EXPERIMENT_MAX_OUTPUT_TOKENS_COT", str(GEMINI_MAX_OUTPUT_TOKENS))
)

POLL_INTERVAL_SECONDS = int(os.environ.get("EXPERIMENT_POLL_INTERVAL", "60"))
POLL_TIMEOUT_HOURS = int(os.environ.get("EXPERIMENT_POLL_TIMEOUT_HOURS", "24"))

# When false, the runner bypasses Gemini Batch and calls the model directly.
USE_BATCH = os.environ.get("EXPERIMENT_USE_BATCH", "true").lower() in {
    "1",
    "true",
    "yes",
}
DIRECT_CONCURRENCY = int(os.environ.get("EXPERIMENT_DIRECT_CONCURRENCY", "6"))

FEW_SHOT_COUNT = int(os.environ.get("EXPERIMENT_FEW_SHOT_COUNT", "2"))

# Vertex AI mode — opt-in via env. When true, the experiment authenticates
# through Application Default Credentials and uses Vertex Batch (which
# requires a GCS bucket for input + output JSONL). Otherwise the experiment
# uses the AI Studio API key path with inline batch requests.
USE_VERTEX = os.environ.get("EXPERIMENT_USE_VERTEX", "false").lower() in {
    "1",
    "true",
    "yes",
}
GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
GCP_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "asia-southeast1")
GCS_BUCKET = os.environ.get("EXPERIMENT_GCS_BUCKET", "")


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "Set GEMINI_API_KEY (or GOOGLE_API_KEY) before running the experiment "
            "in AI Studio mode (or set EXPERIMENT_USE_VERTEX=true with the Vertex "
            "env block)."
        )
    return key


def assert_vertex_config() -> None:
    """Raise if EXPERIMENT_USE_VERTEX=true but project/location/bucket missing."""
    missing = [
        name
        for name, val in [
            ("GOOGLE_CLOUD_PROJECT", GCP_PROJECT),
            ("GOOGLE_CLOUD_LOCATION", GCP_LOCATION),
            ("EXPERIMENT_GCS_BUCKET", GCS_BUCKET),
        ]
        if not val
    ]
    if missing:
        raise RuntimeError(
            "EXPERIMENT_USE_VERTEX=true requires " + ", ".join(missing) + ". "
            "See experiments/RUNBOOK.md § Vertex Batch setup."
        )
