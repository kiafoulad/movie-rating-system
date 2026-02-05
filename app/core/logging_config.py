from __future__ import annotations
import logging.config

_CONFIGURED = False

def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    LOG_FILE = "app.log"

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
                "formatter": "default",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "movie_rating": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            }
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "WARNING",
        },
    })
    _CONFIGURED = True