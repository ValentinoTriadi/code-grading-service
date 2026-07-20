import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with a consistent format for the whole app."""
    fmt = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        datefmt=datefmt,
        stream=sys.stdout,
        force=True,
    )

    # Quieten noisy third-party loggers
    for noisy in ("httpx", "httpcore", "openai", "google"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
