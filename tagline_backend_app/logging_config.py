import logging
import logging.config
import sys

from tagline_backend_app.config import Settings


def setup_logging(settings: Settings):
    """Configure logging for the application."""

    log_level = settings.LOG_LEVEL.upper()
    if log_level not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]:
        print(
            f"Warning: Invalid LOG_LEVEL '{settings.LOG_LEVEL}'. Defaulting to INFO.",
            file=sys.stderr,
        )
        log_level = "INFO"

    # Base configuration for libraries (e.g., httpx, sqlalchemy)
    # Set a higher level by default to reduce noise
    base_lib_level = "WARNING"
    # Allow specific override for debug purposes if needed
    if log_level == "DEBUG":
        base_lib_level = "INFO"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(levelname)-8s %(name)-12s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr",  # Changed to stderr for logs
            },
        },
        "loggers": {
            # Root logger
            "": {
                "level": log_level,
                "handlers": ["console"],
            },
            # Specific library loggers (set higher level)
            "uvicorn": {
                "level": base_lib_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": base_lib_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": base_lib_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": base_lib_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "alembic": {
                "level": base_lib_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "httpx": {
                "level": base_lib_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "dropbox": {
                "level": base_lib_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Our application logger
            "tagline_backend_app": {
                "level": log_level,  # Inherits from root or explicit
                "handlers": ["console"],
                "propagate": False,  # Don't pass to root logger if handled here
            },
        },
    }

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
