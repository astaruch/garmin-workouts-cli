
def kph_to_mps(kph):
    """
    Returns for the given kilometers per hour
    number, meters per second.
    """
    return (kph * 1000) / 3600


def pace_to_mps(pace):
    """
    For the given pace (km/min in format mm:ss),
    returns meters per seconds.
    """
    return 1000 / (pace.mins * 60 + pace.secs)

def mps_to_pace(mps):
    """
    For the given meters per seconds,
    return minutes per km (in float format)
    """
    return 1000 / (60 * mps)

class Pace:
    def __init__(self, minutes, seconds):
        self.mins = minutes
        self.secs = seconds


class IntensityTarget:
    def __init__(self, id, key, val1=None, val2=None, zone=None):
        self.targetType = {
            "workoutTargetTypeId": id,
            "workoutTargetTypeKey": key
        }
        self.targetValueOne = val1
        self.targetValueTwo = val2
        self.zoneNumber = zone


class NoTarget(IntensityTarget):
    def __init__(self):
        super().__init__(1, "no.target")


class CadenceTarget(IntensityTarget):
    def __init__(self, low_cadence, high_cadence):
        super().__init__(3, "cadence", val1=str(low_cadence),
                         val2=str(high_cadence))


class HRZoneTarget(IntensityTarget):
    def __init__(self, low_hr="", high_hr="", zone=None):
        super().__init__(4, "heart.rate.zone", val1=str(low_hr),
                         val2=str(high_hr), zone=str(zone))


class HRZone1Target(HRZoneTarget):
    def __init__(self):
        super().__init__(zone=1)


class HRZone2Target(HRZoneTarget):
    def __init__(self):
        super().__init__(zone=2)


class HRZone3Target(HRZoneTarget):
    def __init__(self):
        super().__init__(zone=3)


class HRZone4Target(HRZoneTarget):
    def __init__(self):
        super().__init__(zone=4)


class HRZone5Target(HRZoneTarget):
    def __init__(self):
        super().__init__(zone=5)


class SpeedTarget(IntensityTarget):
    def __init__(self, low_kph, high_kph):
        low_mps = kph_to_mps(low_kph)
        high_mps = kph_to_mps(high_kph)
        super().__init__(5, "speed.zone", val1=low_mps,
                         val2=high_mps)


class PaceTarget(IntensityTarget):
    def __init__(self, low_pace, high_pace):
        low_mps = pace_to_mps(low_pace)
        high_mps = pace_to_mps(high_pace)
        super().__init__(6, "pace.zone", val1=low_mps,
                         val2=high_mps)
