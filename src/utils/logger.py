"""Logging system: writes all actions and errors to logs/app.log."""

import logging
import os

LOGGER_NAME = "student_info_system"


def setup_logger(log_file: str) -> logging.Logger:
    """Create the app logger that writes to `log_file`.

    The logs folder is created automatically if it does not exist.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)

    # Remove old handlers so repeated calls never create duplicate lines
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handler = logging.FileHandler(log_file, encoding="utf-8")
    except OSError as exc:
        # Graceful fallback: keep logging, but to the console only
        print(f"Warning: cannot write log file ({exc}). Logging to console.")
        handler = logging.StreamHandler()

    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    """Return the shared app logger."""
    return logging.getLogger(LOGGER_NAME)
