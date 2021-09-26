import logging
import json
import yaml

from login import Login
from libs.parser import WorkoutParser

log = logging.getLogger(__name__)


class Import():
    def __init__(self, args):
        login = Login()
        login.login()
        self.session = login.get_session()
        self.filename = args.import_file

        self.import_workouts()

    def import_workouts(self):
        workout_obj = self.parse_yaml_file(self.filename)

        workout_parser = WorkoutParser(own_format=workout_obj)
        garmin_workout = workout_parser.get_garmin_format()

        workout_json = json.dumps(garmin_workout, sort_keys=True, indent=2)

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
