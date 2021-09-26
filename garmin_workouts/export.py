import logging
import json
import time
import yaml

from typing import List

from login import Login
from libs.parser import WorkoutParser


log = logging.getLogger(__name__)


class Export():
    def __init__(self, args):
        self.export_type = args.export_type if args.export_type else 'yaml'
        login = Login()
        login.login()
        self.session = login.get_session()
        if args.export_sort == 'asc':
            self.order_seq = 'ASC'
        else:
            self.order_seq = 'DESC'
        self.limit = args.export_limit if 'export_limit' in args else 999
        self.stdout = not args.export_file and args.export_file != ''
        if args.export_file != '':
            self.filename = args.export_file
        else:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            if self.export_type == 'yml':
                extension = 'yml'
            else:
                extension = 'json'
            self.filename = f'workouts_{timestamp}.{extension}'

        self.export()

    def export(self):
        if self.export_type == 'json':
            self.export_json()
        elif self.export_type == 'raw':
            self.export_raw()
        elif self.export_type == 'yml':
            self.export_yml()
        else:
            self.export_one_workout_to_yml()
            # raise NotImplementedError

    def get_workouts_info(self):
        workouts_url = "https://connect.garmin.com/proxy/workout-service/workouts"
        workouts_params = {
            "start": 1,
            "limit": self.limit,
            "myWorkoutsOnly": True,
            "sharedWorkoutsOnly": False,
            "orderBy": "WORKOUT_NAME",
            "orderSeq": self.order_seq,
            "includeAtp": False,
        }
        workouts_response = self.session.get(
            url=workouts_url,
            params=workouts_params)
        workouts_response.raise_for_status()

        return json.loads(workouts_response.text)

    def export_json(self):
        print(123)

    def get_workouts_ids(self) -> List[int]:
        response_json = self.get_workouts_info()
        # log.debug(print(json.dumps(response_json, indent=2)))
        ids = []

        for workout in response_json:
            if workout and "workoutId" in workout:
                ids.append(workout["workoutId"])
        return ids

    def get_workout(self, workout_id):
        base_url = "https://connect.garmin.com/proxy/workout-service/workout"
        workout_url = f'{base_url}/{workout_id}'
        workout_response = self.session.get(workout_url)

        return json.loads(workout_response.text)

    def export_raw(self):
        workouts_id = self.get_workouts_ids()

        print(workouts_id)
        workouts = []
        for wid in workouts_id:
            workouts.append(self.get_workout(wid))

        if self.stdout:
            print(json.dumps(workouts, indent=2))
        else:
            with open(self.filename, 'w') as outfile:
                log.info('Storing workouts to the %s' % self.filename)
                json.dump(workouts, outfile, indent=2)

    def export_yml(self):
        raise NotImplementedError

    def export_one_workout_to_yml(self):
        self.limit = 1
        workout_id = self.get_workouts_ids()[0]

        workout = self.get_workout(workout_id)

        try:
            workout_parser = WorkoutParser(garmin_format=workout)
            workout_instance = workout_parser.get_own_format()
        except Exception as err:
            print("Problem with parsing")
            print(json.dumps(workout, indent=2))
            print(workout)
            raise err

        # print(workout_instance)
        print(yaml.dump(workout_instance, default_flow_style=False))
