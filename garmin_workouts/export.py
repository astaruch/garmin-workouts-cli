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
            self.filename = f'workouts_{timestamp}.yml'

    def export(self):
        if self.export_type == 'yml':
            self.export_yml()
        else:
            self.export_one_workout_to_yml()
            # raise NotImplementedError

    def get_workouts_ids(self) -> List[int]:
        response_json = self.api_client.get_workouts_info(self.limit, self.order_seq)
        # log.debug(print(json.dumps(response_json, indent=2)))
        ids = []

        for workout in response_json:
            if workout and "workoutId" in workout:
                ids.append(workout["workoutId"])
        return ids

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
