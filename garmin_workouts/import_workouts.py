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
        self._save_to_file = args.import_save_to_file
        self.import_workouts()

    def import_workouts(self):
        workout_obj = self.parse_yaml_file(self.filename)

        workout_parser = WorkoutParser(own_format=workout_obj)
        garmin_workout = workout_parser.get_garmin_format()
        workout_name = workout_parser.get_workout_name()
        workout_id = workout_parser.get_workout_id()

        workout_json = json.dumps(garmin_workout, sort_keys=True, indent=2)

        log.debug(json.dumps(garmin_workout, sort_keys=True, indent=2))

        if workout_id:
            self.api_client.update_existing_workout(workout_json,
                                                    workout_name,
                                                    workout_id)
        else:
            workout_id, _ = self.api_client.upload_new_workout(workout_json, workout_name)

        workout_parser.set_workout_id(workout_id)
        # Store the uploaded workout into the YAML file, so we can use
        # it for the future. Use the workout ID in the name
        if self._save_to_file:
            stored_workout_name = f'workout_{workout_id}.yml'
            with open(stored_workout_name, 'w') as outfile:
                yaml.safe_dump(data=workout_parser.get_own_format(),
                               default_flow_style=False,
                               stream=outfile)
                log.info('Workout saved to "%s"' % stored_workout_name)

    def parse_yaml_file(self, filename):
        with open(filename, 'r') as infile:
            log.info(f'Opening file {filename} for reading')
            workout_obj = yaml.safe_load(infile)

        return workout_obj
