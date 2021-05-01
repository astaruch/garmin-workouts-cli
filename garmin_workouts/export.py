import logging
import json
import time

from login import Login

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

    def export(self):
        if self.export_type == 'json':
            self.export_json()
        elif self.export_type == 'raw':
            self.export_raw()
        elif self.export_type == 'yml':
            self.export_yml()
        else:
            raise NotImplementedError

    def download_workouts(self):
        workouts_url = "https://connect.garmin.com/modern/proxy/workout-service/workouts"
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

    def export_raw(self):
        response_jsons = self.download_workouts()

        if self.stdout:
            print(json.dumps(response_jsons, indent=2))
        else:
            with open(self.filename, 'w') as outfile:
                log.info('Storing workouts to the %s' % self.filename)
                json.dump(response_jsons, outfile, indent=2)

    def export_yml(self):
        raise NotImplementedError
