import logging
import sys

# Module-level logger name used across the application
LOGGER_NAME = "movie_rating"


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure the application-wide logging.

    Notes:
    - Uses a StreamHandler to output logs to stdout.
    - Keeps configuration idempotent (does not add duplicate handlers).
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)

    # Prevent duplicate handlers if setup_logging() is called multiple times
    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False


def get_logger() -> logging.Logger:
    """
    Get the application logger.
    Call setup_logging() once at application startup before using the logger.
    """
    return logging.getLogger(LOGGER_NAME)
