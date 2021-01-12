import json
import random

from workouts.duration import CaloriesDuration
from workouts.duration import DistanceDuration
from workouts.duration import HRDuration
from workouts.duration import LapButtonDuration
from workouts.duration import TimeDuration

from workouts.step import CooldownStep
from workouts.step import IntervalStep
from workouts.step import OtherStep
from workouts.step import RecoveryStep
from workouts.step import RepeatStep
from workouts.step import RestStep
from workouts.step import WarmupStep

from workouts.target import Pace

from workouts.target import CadenceTarget
from workouts.target import HRZone1Target
from workouts.target import HRZone2Target
from workouts.target import HRZone3Target
from workouts.target import HRZone4Target
from workouts.target import HRZone5Target
from workouts.target import HRZoneTarget
from workouts.target import NoTarget
from workouts.target import PaceTarget
from workouts.target import SpeedTarget


class WorkoutStep:
    def __init__(self, step_order, step_type, end_condition, target_type):
        assert step_order
        assert step_type
        assert end_condition
        assert target_type

        self.stepId = None
        self.stepOrder = step_order
        self.childStepId = None
        self.description = None

        self.type = step_type.type
        self.stepType = step_type.stepType

        self.endCondition = end_condition.endCondition
        self.preferredEndConditionUnit = end_condition. \
            preferredEndConditionUnit
        self.endConditionValue = end_condition.endConditionValue
        self.endConditionCompare = end_condition.endConditionCompare
        self.endConditionZone = end_condition.endConditionZone

        self.targetType = target_type.targetType
        self.targetValueOne = target_type.targetValueOne
        self.targetValueTwo = target_type.targetValueTwo
        self.zoneNumber = target_type.zoneNumber


class Workout(object):
    def __init__(self, name=None):
        self.workoutName = name

    def generate_sample_workout(self):
        self.sportType = {
            "sportTypeId": 1,
            "sportTypeKey": "running"
        }
        if not self.workoutName:
            self.workoutName = self.get_random_name()
        self.workoutSegments = [
            {
                "segmentOrder": 1,
                "sportType": {
                    "sportTypeId": 1,
                    "sportTypeKey": "running",
                },
                "workoutSteps": [
                    WorkoutStep(
                        1,
                        WarmupStep(),
                        TimeDuration(1, 0),
                        NoTarget()
                        # TimeDuration(1, 10),
                        # PaceTarget(Pace(5, 30), Pace(6, 0))
                    ),
                ]
            }
        ]

    def toJSON(self, indent=4):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=indent)

    @staticmethod
    def get_random_name():
        rnd_hash = random.getrandbits(24)
        return 'Workout %x' % rnd_hash
