import json
import logging

from login import Login

from workouts.workout import Workout

log = logging.getLogger(__name__)


class Create:
    def __init__(self, args):
        if 'workout_name' in args and args.workout_name:
            self.name = args.workout_name
        else:
            self.name = Workout.get_random_name()

        self.filename = f"{self.name.replace(' ', '_')}.json"
        self.response_filename = f"{self.name.replace(' ', '_')}_response.json"

        self.keep = args.keep_json

        self.dont_upload = args.no_upload
        if not self.dont_upload:
            login_module = Login()
            login_module.login()
            self.session = login_module.get_session()

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
            assert self.session

            log.info(f"Uploading a new workout '{self.name}' to the Garmin Connect")
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "NK": "NT",
                "Referer": "https://connect.garmin.com/modern/workouts",
                "Content-Type": "application/json",
            }
            response = self.session.post(
                "https://connect.garmin.com/modern/proxy/workout-service/workout",
                headers=headers, data=workout.toJSON(None))
            response.raise_for_status()

            response_json = response.json()
            new_workout_url = f"https://connect.garmin.com/modern/workout/{response_json['workoutId']}"
            log.info(f'New workout created: {new_workout_url}')

            if self.keep:
                with open(self.response_filename, 'w') as outfile:
                    log.debug('Storing response to the %s'
                              % self.response_filename)
                    json.dump(response_json, outfile, indent=4)
