"""General utility functions."""
# pylint: disable=E0401
from datetime import datetime

# pylint: enable=E0401


def csharp_ticks(date_time: datetime = datetime.utcnow(), short: bool = False) -> int:
    """Python implementation of C# DateTime.UtcNow.Ticks.

    Args:
        date_time (datetime, optional): The datetime to convert to ticks. Defaults to datetime.utcnow().
        short (bool, optional): Whether to return the short ticks. Defaults to False.

    Returns:
        int: The ticks.
    """

    _ticks = (date_time - datetime(1, 1, 1)).total_seconds()

    if short:
        return int(_ticks)

    return int(_ticks * (10**7))
