from datetime import datetime, time
import pytz

ET = pytz.timezone("US/Eastern")


def seconds_from_open(now: datetime) -> int:
    """
    Seconds elapsed since 09:30:00 ET market open.

    Returns:
    - 0 for any time before open
    - Non-negative integer
    """
    et = now.astimezone(ET)
    open_time = et.replace(
        hour=9,
        minute=30,
        second=0,
        microsecond=0,
    )

    delta = (et - open_time).total_seconds()
    return max(0, int(delta))