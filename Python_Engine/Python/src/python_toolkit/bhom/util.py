"""General utility functions."""
# pylint: disable=E0401
from datetime import datetime, timedelta, timezone
import pandas as pd
from typing import Union
# pylint: enable=E0401


def bson_unix_ticks(date_time: Union[datetime, pd.Timestamp] = None, short: bool = False) -> int:
    """Python implementation of unix ticks.

    Args:
        date_time (datetime, optional): The datetime to convert to ticks. Defaults to datetime.now(timezone.utc).
        short (bool, optional): Whether to return the short ticks. Defaults to False.

    Returns:
        int: The ticks.
    """

    if isinstance(date_time, pd.Timestamp):
        date_time = date_time.tz_convert() #This throws an error if the pandas timestamp is not timezone aware. If no error the resultant date_time will be in UTC.
        date_time = date_time.to_pydatetime().replace(tzinfo=timezone.utc) #Convert to python datetime and ensure it is a timezone aware with timestamp set to UTC.

    date_time = date_time or datetime.now(timezone.utc)

    _ticks = (date_time - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds() * 10**3

    if short:
        return int(_ticks)

    return int(_ticks*(10**3))

def bson_unix_ticks_to_datetime(ticks: int, short:bool = False) -> datetime:

    if not short:
        ticks = int(ticks / (10**3))

    return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=ticks)

