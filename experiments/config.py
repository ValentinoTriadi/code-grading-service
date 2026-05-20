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

POLL_INTERVAL_SECONDS = int(os.environ.get("EXPERIMENT_POLL_INTERVAL", "60"))
POLL_TIMEOUT_HOURS = int(os.environ.get("EXPERIMENT_POLL_TIMEOUT_HOURS", "24"))

FEW_SHOT_COUNT = int(os.environ.get("EXPERIMENT_FEW_SHOT_COUNT", "2"))


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "Set GEMINI_API_KEY (or GOOGLE_API_KEY) before running the experiment."
        )
    return key
