"""General utility functions."""
# pylint: disable=E0401
from datetime import datetime, timedelta
# pylint: enable=E0401


def bson_unix_ticks(date_time: datetime = datetime.utcnow(), short: bool = False) -> int:
    """Python implementation of unix ticks.

    Args:
        date_time (datetime, optional): The datetime to convert to ticks. Defaults to datetime.utcnow().
        short (bool, optional): Whether to return the short ticks. Defaults to False.

    Returns:
        int: The ticks.
    """

    _ticks = (date_time - datetime(1970, 1, 1)).total_seconds() * 10**3

    if short:
        return int(_ticks)

    return int(_ticks*(10**3))

def bson_unix_ticks_to_datetime(ticks: int, short:bool = False) -> datetime:

    if not short:
        ticks = int(ticks / (10**3))

    return datetime(1970, 1, 1) + timedelta(milliseconds=ticks)

