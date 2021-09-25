
from libs.conversions import mps_to_pace_string

from libs.exception import \
    GarminConnectObjectError, \
    GarminConnectNotImplementedError


class WorkoutParser():
    """
    Object for parsing the objects comming from:
    - Garmin Connect API JSON
    - or the own format, used for YAML human readable serialization
    """

    def __init__(self,
                 garmin_format=None,
                 own_format=None):
        # type: (dict, dict) -> None
        self._garmin_format = garmin_format
        self._own_format = own_format
        self.parse()

    def get_garmin_format(self):
        return self._garmin_format

    def get_own_format(self):
        return self._own_format

    def parse(self):
        # type: (None) -> None
        """
        Parses the input data and fills every other format for later usage.
        """
        if self._garmin_format:
            own_format = self.parse_garmin_format(self._garmin_format)
            self._own_format = own_format
        elif self._own_format:
            garmin_format = self.parse_own_format(self._own_format)
            self._garmin_format = garmin_format
        else:
            raise ValueError("Unexpected arguments for WorkoutParser")

    def parse_garmin_format(self, garmin):
        # type: (dict) -> dict
        """
        Parses the Garmin Connect API object and return dictionary in
        our own format.
        """
        own = {}

        if "workoutName" not in garmin:
            raise GarminConnectObjectError("workoutName", garmin)
        own["name"] = garmin["workoutName"]

        if "workoutSegments" not in garmin:
            raise GarminConnectObjectError("workoutSegments", garmin)

        workout_segments = garmin["workoutSegments"]

        for segment in workout_segments:
            if "sportType" not in segment:
                raise GarminConnectObjectError("sportType", segment)
            sport = segment["sportType"]["sportTypeKey"]
            if sport == "running":
                if "workoutSteps" not in segment:
                    raise GarminConnectObjectError("workoutSteps", segment)
                workout_steps = segment["workoutSteps"]
                own_steps = []
                for workout_step in workout_steps:
                    own_step = \
                        self.parse_garmin_format_running_step(workout_step)
                    own_steps.append(own_step)
                own["steps"] = own_steps
                return own
            else:
                raise GarminConnectNotImplementedError("sportType", sport,
                                                       segment)

        raise Exception("Shouldn't be reachable")

    def parse_garmin_format_running_step(self, garmin_step):
        # type: (dict) -> dict
        """
        Parses one running step from Garmin Connect API and return it
        in our own format.
        """
        own_step = {}
        if "type" not in garmin_step:
            raise GarminConnectObjectError("type", garmin_step)

        type = garmin_step["type"]

        if type == "RepeatGroupDTO":
            own_step["type"] = "repetition"

            if "numberOfIterations" not in garmin_step:
                raise GarminConnectObjectError("numberOfIterations",
                                               garmin_step)
            own_step["count"] = garmin_step["numberOfIterations"]
            if "workoutSteps" not in garmin_step:
                raise GarminConnectObjectError("workoutSteps", garmin_step)

            garmin_substeps = garmin_step["workoutSteps"]
            own_substeps = []
            for garmin_substep in garmin_substeps:
                own_substep = self. \
                    parse_garmin_format_running_step(garmin_substep)
                own_substeps.append(own_substep)
            own_step["steps"] = own_substeps
        elif type == "ExecutableStepDTO":
            if "stepType" not in garmin_step:
                raise GarminConnectObjectError("stepType", garmin_step)

            step_type = garmin_step["stepType"]["stepTypeKey"]
            if step_type == "interval":
                own_step["type"] = "run"
            elif step_type == "recovery":
                own_step["type"] = "recovery"
            else:
                raise GarminConnectNotImplementedError("stepTypeKey",
                                                       step_type,
                                                       garmin_step)

            if "endCondition" not in garmin_step:
                raise GarminConnectObjectError("endCondition", garmin_step)

            duration_type = garmin_step["endCondition"]["conditionTypeKey"]
            if duration_type == "distance":
                distance = garmin_step["endConditionValue"]
                own_step["distance"] = distance
            elif duration_type == "lap.button":
                own_step["lap_button"] = True
            else:
                raise GarminConnectNotImplementedError("conditionTypeKey",
                                                       duration_type,
                                                       garmin_step)

            if "targetType" not in garmin_step:
                raise GarminConnectObjectError("targetType", garmin_step)

            target_type = garmin_step["targetType"]["workoutTargetTypeKey"]
            if target_type == "pace.zone":
                if "targetValueOne" not in garmin_step:
                    raise GarminConnectObjectError("targetValueOne",
                                                   garmin_step)
                if "targetValueTwo" not in garmin_step:
                    raise GarminConnectObjectError("targetValueTwo",
                                                   garmin_step)

                pace_from = mps_to_pace_string(garmin_step["targetValueOne"])
                pace_to = mps_to_pace_string(garmin_step["targetValueTwo"])

                own_step["pace_from"] = pace_from
                own_step["pace_to"] = pace_to
            elif target_type == "no.target":
                pass
            else:
                raise GarminConnectNotImplementedError("workoutTargetTypeKey",
                                                       target_type,
                                                       garmin_step)
        else:
            raise GarminConnectNotImplementedError("type",
                                                   type,
                                                   garmin_step)

        return own_step
