"""Logging utilities for BHoM analytics."""

# pylint: disable=E0401
import logging
import sys

# pylint: enable=E0401

from .. import TOOLKIT_NAME

level = logging.INFO

formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(level)
handler.setFormatter(formatter)

CONSOLE_LOGGER = logging.getLogger(f"{TOOLKIT_NAME}[console]")
CONSOLE_LOGGER.propagate = False
CONSOLE_LOGGER.setLevel(level)
CONSOLE_LOGGER.addHandler(handler)
