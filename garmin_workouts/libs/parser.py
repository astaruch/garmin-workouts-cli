
import logging


from libs.conversions import \
    mps_to_pace_string, \
    pace_string_to_mps, \
    seconds_to_time_string, \
    mps_to_kmh_string
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
                 own_format=None,
                 append_to_log=None):
        # type: (dict, dict) -> None
        self._garmin_format = garmin_format
        self._own_format = own_format
        self._append_to_log = append_to_log
        self.parse()

    def get_garmin_format(self):
        return self._garmin_format

    def get_own_format(self):
        return self._own_format

    def get_workout_name(self):
        assert self._own_format
        return self._own_format["name"]

    def get_workout_id(self):
        if "id" in self._own_format:
            return self._own_format["id"]
        else:
            return None

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
        if self._append_to_log:
            log.info(f"Parsing Garmin Connect API object.. {self._append_to_log}")
        else:
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
            if step_type == "warmup":
                own_step["type"] = "warmup"
            elif step_type == "cooldown":
                own_step["type"] = "cooldown"
            elif step_type == "interval":
                own_step["type"] = "run"
            elif step_type == "recovery":
                own_step["type"] = "recovery"
            elif step_type == "rest":
                own_step["type"] = "rest"
            elif step_type == "other":
                own_step["type"] = "other"
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
            elif duration_type == "time":
                seconds = garmin_step["endConditionValue"]
                own_step["time"] = seconds_to_time_string(seconds)
            elif duration_type == "calories":
                own_step["calories"] = garmin_step["endConditionValue"]
            elif duration_type == "heart.rate":
                hr = garmin_step["endConditionValue"]
                hr_compare = garmin_step["endConditionCompare"]
                if hr_compare == "lt":
                    own_step["hr_below"] = hr
                elif hr_compare == "gt":
                    own_step["hr_above"] = hr
                else:
                    raise GarminConnectNotImplementedError("endConditionCompare",
                                                           hr_compare,
                                                           garmin_step)
            else:
                raise GarminConnectNotImplementedError("conditionTypeKey",
                                                       duration_type,
                                                       garmin_step)

            if "targetType" not in garmin_step:
                raise GarminConnectObjectError("targetType", garmin_step)

            if not garmin_step["targetType"]:
                # we don't nede to have target type. bare step
                pass
            else:
                if "workoutTargetTypeKey" not in garmin_step["targetType"]:
                    raise GarminConnectObjectError("workoutTargetTypeKey", garmin_step)

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
                elif target_type == "heart.rate.zone":
                    if ("zoneNumber" in garmin_step and
                            garmin_step["zoneNumber"] is not None):
                        # We have a precise zone number
                        hr_zone = garmin_step["zoneNumber"]
                        own_step["hr_zone"] = hr_zone
                    else:
                        # We have a zone range with the 2 values
                        hr_low = garmin_step["targetValueOne"]
                        hr_high = garmin_step["targetValueTwo"]
                        own_step["hr_low"] = hr_low
                        own_step["hr_high"] = hr_high
                elif target_type == "speed.zone":
                    if "targetValueOne" not in garmin_step:
                        raise GarminConnectObjectError("targetValueOne",
                                                    garmin_step)
                    if "targetValueTwo" not in garmin_step:
                        raise GarminConnectObjectError("targetValueTwo",
                                                    garmin_step)
                    speed_from = mps_to_kmh_string(garmin_step["targetValueOne"])
                    speed_to = mps_to_kmh_string(garmin_step["targetValueTwo"])

                    own_step["pace_from"] = speed_from
                    own_step["pace_to"] = speed_to
                elif target_type == "cadence":
                    if "targetValueOne" not in garmin_step:
                        raise GarminConnectObjectError("targetValueOne",
                                                    garmin_step)
                    if "targetValueTwo" not in garmin_step:
                        raise GarminConnectObjectError("targetValueTwo",
                                                    garmin_step)

                    own_step["cadence_from"] = garmin_step["targetValueOne"]
                    own_step["cadence_to"] = garmin_step["targetValueTwo"]
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
        elif type == "run" or "recovery" or "warmup" or "cooldown":
            garmin_step["type"] = "ExecutableStepDTO"

            # Set the type of the Garmin run
            if type == "warmup":
                garmin_step["stepType"] = {
                    "stepTypeId": 1,
                    "stepTypeKey": "warmup"
                }
            elif type == "cooldown":
                garmin_step["stepType"] = {
                    "stepTypeId": 2,
                    "stepTypeKey": "cooldown"
                }
            elif type == "run":
                garmin_step["stepType"] = {
                    "stepTypeId": 3,
                    "stepTypeKey": "interval"
                }
            elif type == "recovery":
                garmin_step["stepType"] = {
                    "stepTypeId": 4,
                    "stepTypeKey": "recovery"
                }
            else:
                raise OwnFormatDataObjectNotImplementedError("type",
                                                             type,
                                                             own_step)

            # Set the distance/duration
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


class WorkoutsInfoParser():
    """
    Object to parse Garmin Connect API info about workout, not the
    workout itself.
    """
    def __init__(self, workout_info):
        self._workout_info = workout_info
        self._own_info = {}
        self._parse()

    def _parse(self):
        log.debug("Parsing Garmin workout info...")
        if "workoutId" not in self._workout_info:
            raise GarminConnectObjectError("workoutId", self._workout_info)
        if "sportType" not in self._workout_info:
            raise GarminConnectObjectError("sportType", self._workout_info)

        self._own_info["id"] = self._workout_info["workoutId"]

        sport_type = self._workout_info["sportType"]["sportTypeKey"]
        if sport_type == "running":
            self._own_info["type"] = "running"
        else:
            raise GarminConnectNotImplementedError("sportType.sportTypeKey",
                                                   sport_type,
                                                   self._workout_info)

    def is_run(self):
        return self._own_info["type"] == "running"

    def get_id(self):
        return self._own_info["id"]
