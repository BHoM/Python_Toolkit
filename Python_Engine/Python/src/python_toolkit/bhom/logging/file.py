"""Logging utilities for BHoM analytics."""

# pylint: disable=E0401
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

# pylint: enable=E0401


from .. import TOOLKIT_NAME, BHOM_LOG_FOLDER

formatter = logging.Formatter("%(message)s")
handler = RotatingFileHandler(
    BHOM_LOG_FOLDER / f"{TOOLKIT_NAME}_{datetime.now().strftime('%Y%m%d')}.log",
    mode="a",
    maxBytes=25 * 1024 * 1024,  # 25mb max before file overwritten
    backupCount=1,
    encoding="utf-8",
    delay=True,  # wait until all logs collected before writing
)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

ANALYTICS_LOGGER = logging.getLogger(f"{TOOLKIT_NAME}")
ANALYTICS_LOGGER.propagate = False
ANALYTICS_LOGGER.setLevel(logging.DEBUG)
ANALYTICS_LOGGER.addHandler(handler)
