
import logging


from libs.conversions import mps_to_pace_string, pace_string_to_mps
from libs.exception import \
    GarminConnectObjectError, \
    GarminConnectNotImplementedError, \
    OwnFormatDataObjectError, \
    OwnFormatDataObjectNotImplementedError

log = logging.getLogger(__name__)


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

    def get_workout_name(self):
        assert self._own_format
        return self._own_format["name"]

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
        log.info("Parsing Garmin Connect API object..")
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

    def parse_own_format(self, own):
        # type: (dict) -> dict
        """
        Parses our own format dictionary, and returns
        dictionary in in Garmin Connect API dictionary format.
        """
        log.info("Parsing own format data object..")
        garmin = {}
        self.step_index = 1

        garmin["sportType"] = {
            "sportTypeId": 1,
            "sportTypeKey": "running"
        }

        if "name" not in own:
            raise OwnFormatDataObjectError("name", own)

        garmin["workoutName"] = own["name"]

        segments = []
        segment_1 = {}
        segment_1["segmentOrder"] = 1
        segment_1["sportType"] = {
            "sportTypeId": 1,
            "sportTypeKey": "running"
        }
        if "steps" not in own:
            raise OwnFormatDataObjectError("steps", own)

        garmin_steps = []
        for own_step in own["steps"]:
            garmin_step = self.parse_own_format_running_step(own_step)
            garmin_steps.append(garmin_step)

        segment_1["workoutSteps"] = garmin_steps
        segments.append(segment_1)
        garmin["workoutSegments"] = segments
        return garmin

    def parse_own_format_running_step(self, own_step):
        # type: (dict) -> dict
        """
        Parses one running step from our own format, and return it
        in Garmin Connect API format dictionary.
        """
        garmin_step = {}
        garmin_step["stepOrder"] = self.step_index
        self.step_index += 1

        if "type" not in own_step:
            raise OwnFormatDataObjectError("type", own_step)

        type = own_step["type"]
        if type == "repetition":
            garmin_step["type"] = "RepeatGroupDTO"
            garmin_step["stepType"] = {
                "stepTypeId": 6,
                "stepTypeKey": "repeat"
            }
            # NOTE: childStepId and smartRepeat both needs to be in the object
            #       otherwise Garmin server throws 500 Internal Error
            # TODO: Check what 'childStepId' is doing.
            garmin_step["childStepId"] = 1
            # TODO: Check what really 'smartRepeat' do
            garmin_step["smartRepeat"] = False
            if "count" not in own_step:
                raise OwnFormatDataObjectError("count", own_step)

            garmin_step["numberOfIterations"] = own_step["count"]

            if "steps" not in own_step:
                raise OwnFormatDataObjectError("steps", own_step)

            garmin_substeps = []
            for own_substep in own_step["steps"]:
                garmin_substep = \
                    self.parse_own_format_running_step(own_substep)
                garmin_substeps.append(garmin_substep)

            garmin_step["workoutSteps"] = garmin_substeps
        elif type == "run" or type == "recovery":
            garmin_step["type"] = "ExecutableStepDTO"

            if type == "run":
                garmin_step["stepType"] = {
                    "stepTypeId": 3,
                    "stepTypeKey": "interval"
                }
            elif type == "recovery":
                garmin_step["stepType"] = {
                    "stepTypeId": 4,
                    "stepTypeKey": "recovery"
                }

            if "lap_button" in own_step:
                garmin_step["endCondition"] = {
                    "conditionTypeId": 1,
                    "conditionTypeKey": "lap.button"
                }
            elif "distance" in own_step:
                garmin_step["endCondition"] = {
                    "conditionTypeId": 3,
                    "conditionTypeKey": "distance"
                }
                distance = own_step["distance"]
                garmin_step["endConditionValue"] = float(distance)
                garmin_step["preferredEndConditionUnit"] = {
                    "unitId": 2,
                    "unitKey": "kilometer",
                    "factor": 100000.0
                }

                if "pace_from" in own_step and "pace_to" not in own_step:
                    raise OwnFormatDataObjectError("pace_to", own_step)
                if "pace_from" not in own_step and "pace_to" in own_step:
                    raise OwnFormatDataObjectError("pace_from", own_step)

                if "pace_from" in own_step and "pace_to" in own_step:
                    pace_from = own_step["pace_from"]
                    pace_to = own_step["pace_to"]
                    mps_from = pace_string_to_mps(pace_from)
                    mps_to = pace_string_to_mps(pace_to)

                    garmin_step["targetType"] = {
                        "workoutTargetTypeId": 6,
                        "workoutTargetTypeKey": "pace.zone",
                    }
                    garmin_step["targetValueOne"] = mps_from
                    garmin_step["targetValueTwo"] = mps_to
        else:
            raise OwnFormatDataObjectNotImplementedError("type",
                                                         type,
                                                         own_step)

        return garmin_step