import logging
import json
import yaml

from libs.parser import WorkoutParser
from libs.garmin_api_client import GarminApiClient

log = logging.getLogger(__name__)


class Import():
    def __init__(self, args, session):

        self.filename = args.import_file
        self.api_client = GarminApiClient(session=session)
        self.import_workouts()

    def import_workouts(self):
        workout_obj = self.parse_yaml_file(self.filename)

        workout_parser = WorkoutParser(own_format=workout_obj)
        garmin_workout = workout_parser.get_garmin_format()
        workout_name = workout_parser.get_workout_name()

        workout_json = json.dumps(garmin_workout, sort_keys=True, indent=2)

        self.api_client.upload_new_workout(workout_json, workout_name)

    def parse_yaml_file(self, filename):
        with open(filename, 'r') as infile:
            log.info(f'Opening file {filename} for reading')
            workout_obj = yaml.load(infile)

        return workout_obj
