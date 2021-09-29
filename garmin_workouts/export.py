import logging
import json
import time
import yaml

from typing import List

from libs.parser import WorkoutParser
from libs.garmin_api_client import GarminApiClient

log = logging.getLogger(__name__)


class Export():
    def __init__(self, args, session):
        self.export_type = args.export_type if args.export_type else 'yaml'
        self._parse_args(args)
        self.api_client = GarminApiClient(session=session)
        self.export()

    def _parse_args(self, args):
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

    def export_json(self):
        print(123)

    def get_workouts_ids(self) -> List[int]:
        response_json = self.api_client.get_workouts_info(self.limit, self.order_seq)
        # log.debug(print(json.dumps(response_json, indent=2)))
        ids = []

        for workout in response_json:
            if workout and "workoutId" in workout:
                ids.append(workout["workoutId"])
        return ids

    def export_raw(self):
        workouts_id = self.get_workouts_ids()

        print(workouts_id)
        workouts = []
        for wid in workouts_id:
            workouts.append(self.api_client.get_workout_details(wid))

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

        workout = self.api_client.get_workout_details(workout_id)

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
