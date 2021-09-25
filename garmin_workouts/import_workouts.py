import logging
import json
import time

import math
import typing
import yaml

from typing import List

from login import Login

log = logging.getLogger(__name__)

def pace_to_mps(pace_string):
    # type: (str) -> None
    """
    For the given pace in (km/min in format mm:ss),
    returns meters per seconds.
    """
    if ' ' in pace_string:
        value, units = pace_string.split()
    else:
        value = pace_string

    if ':' not in value:
        raise ValueError("missing ':' in the pace. Expected pace in format 'MM:SS', got: ", value)
    minutes, seconds = value.split(':')

    return 1000 / (int(minutes) * 60 + int(seconds))


class Import():
    def __init__(self, args):
        login = Login()
        login.login()
        self.session = login.get_session()
        self.filename = args.import_file

        self.import_workouts()

    def import_workouts(self):
        workout_obj = self.parse_yaml_file(self.filename)

        workout_json_obj = self.create_workout_json(workout_obj)
        workout_json = json.dumps(workout_json_obj, sort_keys=True, indent=2)

        assert self.session

        log.info(f"Importing a workout from file {self.filename} to the Garmin Connect")
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "NK": "NT",
            "Referer": "https://connect.garmin.com/modern/workouts",
            "Content-Type": "application/json",
        }
        response = self.session.post(
            "https://connect.garmin.com/modern/proxy/workout-service/workout",
            headers=headers, data=workout_json)
        response.raise_for_status()

        response_json = response.json()
        new_workout_url = f"https://connect.garmin.com/modern/workout/{response_json['workoutId']}"
        log.info(f'New workout created: {new_workout_url}')

        # if self.keep:
        #     with open(self.response_filename, 'w') as outfile:
        #         log.debug('Storing response to the %s'
        #                     % self.response_filename)
        #         json.dump(response_json, outfile, indent=4)

    def parse_yaml_file(self, filename):
        with open(filename, 'r') as infile:
            log.info(f'Openin file {filename} for reading')
            workout_obj = yaml.load(infile)

        return workout_obj

    def create_workout_json(self, obj):
        if 'run' in obj:
            run_workout = self.create_run_json(obj["run"])

        return run_workout

    def create_run_json(self, obj):
        self.step_index = 1

        run = {}
        run["sportType"] = {
            "sportTypeId": 1,
            "sportTypeKey": "running"
        }
        if "name" not in obj:
            raise ValueError("missing name of workout")
        run["workoutName"] = obj["name"]
        segments = []
        segment_1 = {}
        segment_1["segmentOrder"] = 1
        segment_1["sportType"] = {
            "sportTypeId": 1,
            "sportTypeKey": "running"
        }
        if "steps" not in obj:
            raise ValueError("missing steps of workout")
        steps = []

        for step_from_yaml in obj["steps"]:
            step = self.create_run_step_json(step_from_yaml)
            print(step)
            steps.append(step)

        segment_1["workoutSteps"] = steps

        segments.append(segment_1)
        run["workoutSegments"] = segments
        return run

    def create_run_step_json(self, step_from_yaml):
        # def __init__(self, step_order, step_type, end_condition, target_type):
        step = {}
        step["stepOrder"] = self.step_index
        self.step_index += 1

        if "type" not in step_from_yaml:
            raise ValueError("missing step in the step:", step_from_yaml)

        type = step_from_yaml["type"]
        if type == "repetition":
            step["type"] = "RepeatGroupDTO"
            step["stepType"] = {
                "stepTypeId": 6,
                "stepTypeKey": "repeat"
            }
            step["childStepId"] = 1
            step["smartRepeat"] = False
            if "count" not in step_from_yaml:
                raise ValueError("missing 'count' in the repetition step:", step_from_yaml)

            count = step_from_yaml["count"]
            step["numberOfIterations"] = count

            if "steps" not in step_from_yaml:
                raise ValueError("missing 'steps' in the repetition step:", step_from_yaml)

            sub_steps = []
            for sub_step_from_yaml in step_from_yaml["steps"]:
                sub_step = self.create_run_step_json(sub_step_from_yaml)
                sub_steps.append(sub_step)
            step["workoutSteps"] = sub_steps
        elif type == "run" or type == "recovery":
            step["type"] = "ExecutableStepDTO"

            if type == "run":
                step["stepType"] = {
                    "stepTypeId": 3,
                    "stepTypeKey": "interval"
                }
            elif type == "recovery":
                step["stepType"] = {
                    "stepTypeId": 4,
                    "stepTypeKey": "recovery"
                }

            if "lap_button" in step_from_yaml:
                step["endCondition"] = {
                    "conditionTypeId": 1,
                    "conditionTypeKey": "lap.button"
                }
            elif "distance" in step_from_yaml:
                step["endCondition"] = {
                    "conditionTypeId": 3,
                    "conditionTypeKey": "distance"
                }
                distance = step_from_yaml["distance"]
                step["endConditionValue"] = float(distance)
                step["preferredEndConditionUnit"] = {
                    "unitId": 2,
                    "unitKey": "kilometer",
                    "factor": 100000.0
                }

                if (("pace_from" in step_from_yaml and "pace_to" not in step_from_yaml) or
                    ("pace_from" not in step_from_yaml and "pace_to" in step_from_yaml)):
                    raise ValueError("missing 'pace_from' or 'pace_to':", step_from_yaml)

                if ("pace_from" in step_from_yaml and "pace_to" in step_from_yaml):
                    pace_from = step_from_yaml["pace_from"]
                    pace_to = step_from_yaml["pace_to"]
                    mps_from = pace_to_mps(pace_from)
                    mps_to = pace_to_mps(pace_to)

                    step["targetType"] = {
                        "workoutTargetTypeId": 6,
                        "workoutTargetTypeKey": "pace.zone",
                    }
                    step["targetValueOne"] = mps_from
                    step["targetValueTwo"] = mps_to
        else:
            raise ValueError("Unknown 'type' of run: ", type)

        return step
