class Duration:
    def __init__(self, condition, value=None, unit=None, compare=None):
        self.endCondition = condition
        self.endConditionValue = value
        self.preferredEndConditionUnit = unit
        self.endConditionCompare = compare
        self.endConditionZone = None


class LapButtonDuration(Duration):
    def __init__(self):
        condition = {
            "conditionTypeId": 1,
            "conditionTypeKey": "lap.button"
        }
        super().__init__(condition=condition)


class TimeDuration(Duration):
    def __init__(self, minutes, seconds):
        condition = {
            "conditionTypeId": 2,
            "conditionTypeKey": "time"
        }
        duration = seconds + 60 * minutes
        super().__init__(condition=condition, value=duration)


class DistanceDuration(Duration):
    def __init__(self, distance, unit):
        meters = 0
        if unit == "km":
            meters = distance * 1000
        elif unit == "mi":
            meters = distance * 1609.344
        elif unit == "m":
            meters = distance
        else:
            raise ValueError('Entered unit has not been recognized')

        condition = {
            "conditionTypeId": 3,
            "conditionTypeKey": "distance"
        }
        super().__init__(condition=condition, value=meters)


class CaloriesDuration(Duration):
    def __init__(self, calories):
        condition = {
            "conditionTypeId": 4,
            "conditionTypeKey": "calories"
        }
        super().__init__(condition=condition, value=calories)


class HRDuration(Duration):
    def __init__(self, hr, above_hr=True):
        condition = {
            "conditionTypeId": 6,
            "conditionTypeKey": "heart.rate"
        }
        compare = 'gt' if above_hr else 'lt'
        super().__init__(condition=condition, value=hr, compare=compare)
