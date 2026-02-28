"""
Centralized logging configuration for the ClickComply backend.

All modules should import `logger` from this file to ensure
consistent formatting and output across the application.
"""

import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "clickcomply") -> logging.Logger:
    """
    Returns a configured logger instance.

    Args:
        name: Logger namespace — typically the module name.

    Returns:
        A logging.Logger with stdout handler and consistent formatting.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    return logger


# Default application-wide logger
logger = get_logger()
