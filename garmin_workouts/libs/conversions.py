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
    Convert meters per s
    econds -> pace min per kilometer

    Return formatted string: "MINS:SECS min/km"
    """
    minutes, seconds = mps_to_min_per_km(mps)
    return f"{minutes}:{seconds} min/km"


def pace_string_to_mps(pace_string):
    # type: (str) -> float
    """
    Convert pace string (MIN:SECS min/km) -> meters per second.

    Return float.
    """
    if ' ' in pace_string:
        value, _ = pace_string.split()
    else:
        value = pace_string

    if ':' not in value:
        raise ValueError("missing symobl':' in the pace. "
                         "Expected pace in format 'MM:SS', got: ", value)
    minutes, seconds = value.split(':')

    return 1000 / (int(minutes) * 60 + int(seconds))


def seconds_to_time_string(total_seconds):
    # type: (float) -> str
    """
    Convert seconds -> "XX:YY:ZZ hours"
                    -> "YY:ZZ minutes"
                    -> "ZZ seconds"
    """
    seconds = int(total_seconds % 60)
    minutes_total = math.floor(total_seconds / 60)
    hours = math.floor(minutes_total / 60)
    minutes = minutes_total - hours * 60
    if hours != 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d} hours"
    elif minutes != 0:
        return f"{minutes:02d}:{seconds:02d} minutes"
    else:
        return f"{seconds:02d} seconds"


def mps_to_kmh_string(mps):
    # type: (float) -> str
    """
    Convert meters per seconds in float to km per hour string.

    E.g. 6.11111116 -> "22.0 km/h"
         6.9444444999999995 -> "25.0 km/h"

         1 m/s = x km/h
         1 m/s = x 1000m/3600s
         1 m/s = x 10m/36s
         36/10 = x
         x = 3.6

    Returns string
    """

    return f"{mps * 3.6:.1f} km/h"
