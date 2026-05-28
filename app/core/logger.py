"""Logger estructurado para Newser Pro Cloud."""

import logging
import sys

from app.core.config import settings


def _create_logger() -> logging.Logger:
    logger = logging.getLogger("newser_pro_cloud")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    return logger


logger = _create_logger()
