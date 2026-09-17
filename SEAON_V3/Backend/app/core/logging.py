"""
Logging configuration — structured, timestamps, level control.
"""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a clean, consistent format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Silence overly chatty libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)