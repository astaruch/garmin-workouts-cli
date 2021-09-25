import math

from typing import Tuple


def mps_to_min_per_km(mps):
    # type: (float) -> Tuple[int, int]
    """
    Convert meters per second -> pace min per kilometer

    Returns tuple of intergers: (MINUTES, SECONDS)
    """
    mins_per_km = 1000 / (60 * mps)
    minutes = math.floor(mins_per_km)
    minutes_rest = mins_per_km - minutes
    seconds = round(60 * minutes_rest)
    return (minutes, seconds)


def mps_to_pace_string(mps):
    # type: (float) -> str
    """
    Convert meters per seconds -> pace min per kilometer

    Return formatted string: "MINS:SECS min/km"
    """
    minutes, seconds = mps_to_min_per_km(mps)
    return f"{minutes}:{seconds} min/km"
