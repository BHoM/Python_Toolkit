"""Logging utilities for BHoM analytics."""

# pylint: disable=E0401
import logging
import sys

# pylint: enable=E0401

from .. import TOOLKIT_NAME

formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

CONSOLE_LOGGER = logging.getLogger(f"{TOOLKIT_NAME}[console]")
CONSOLE_LOGGER.propagate = False
CONSOLE_LOGGER.setLevel(logging.DEBUG)
CONSOLE_LOGGER.addHandler(handler)
