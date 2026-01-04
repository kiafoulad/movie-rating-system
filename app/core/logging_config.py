from __future__ import annotations

import logging.config

_CONFIGURED = False


def setup_logging() -> None:
    """
    Minimal stdout logging configuration for Phase 2.
    Idempotent: safe to call multiple times (e.g., reload).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    # With logger name "movie_rating", output matches:
                    # %(asctime)s - movie_rating - %(levelname)s - %(message)s
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "loggers": {
                "movie_rating": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": False,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": "WARNING",
            },
        }
    )

    _CONFIGURED = True
