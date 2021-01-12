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

    def export(self):
        if self.export_type == 'json':
            self.export_json()
        elif self.export_type == 'raw':
            self.export_raw()
        else:
            raise NotImplementedError

    def export_raw(self):
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

        response_jsons = json.loads(workouts_response.text)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f'workouts_{timestamp}.json'
        with open(filename, 'w') as outfile:
            log.info('Storing workouts to the %s' % filename)
            json.dump(response_jsons, outfile, indent=2)
