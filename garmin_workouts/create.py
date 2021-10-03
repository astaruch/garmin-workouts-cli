import json
import logging

from login import Login

from workouts.workout import Workout

from libs.garmin_api_client import GarminApiClient

log = logging.getLogger(__name__)


class Create:
    def __init__(self, args, session):
        self.api_client = GarminApiClient(session=session)

        if 'workout_name' in args and args.workout_name:
            self.name = args.workout_name
        else:
            self.name = Workout.get_random_name()

        self.filename = f"{self.name.replace(' ', '_')}.json"
        self.response_filename = f"{self.name.replace(' ', '_')}_response.json"

        self.keep = args.keep_json

        self.dont_upload = args.no_upload

        if args.sample_workout:
            self.create_sample_workout()

    def create_sample_workout(self):
        workout = Workout(self.name)
        workout.generate_sample_workout()

        if self.keep:
            with open(self.filename, 'w') as outfile:
                log.info('Storing a new workout to the %s' % self.filename)
                outfile.write(workout.toJSON())

        if not self.dont_upload:
            response_json = self.api_client.upload_new_workout(workout.toJSON(indent=None), self.name)

            if self.keep:
                with open(self.response_filename, 'w') as outfile:
                    log.debug('Storing response to the %s'
                              % self.response_filename)
                    json.dump(response_json, outfile, indent=4)
