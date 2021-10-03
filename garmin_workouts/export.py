import logging
import time
import yaml
import json

from libs.parser import WorkoutParser, WorkoutsInfoParser
from libs.garmin_api_client import GarminApiClient

from libs.exception import GarminConnectNotImplementedError

log = logging.getLogger(__name__)


class Export():
    def __init__(self, args, session):
        self._parse_args(args)
        self.api_client = GarminApiClient(session=session)
        self._export()

    def _parse_args(self, args):
        self._export_runs = args.export_runs
        if args.export_garmin_workouts_file:
            self._from_garmin_workouts_file = args.export_garmin_workouts_file
        else:
            self._from_garmin_workouts_file = None

        # TODO: Add comparision in future for bikes and swimming, so it will
        #       emulate --all option
        if not self._export_runs:
            self._export_runs = True
            # and not self._export_cyclings and not self._export_swimmings:
            # self._export_cyclings = True
            # self._export_swimmings = True

        if args.export_sort == 'asc':
            self.order_seq = 'ASC'
        else:
            self.order_seq = 'DESC'
        self.limit = args.export_limit if 'export_limit' in args else 999
        self.stdout = args.export_stdout
        if not self.stdout:
            if not args.export_file:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                self.filename = f'workouts_{timestamp}.yml'
            else:
                self.filename = args.export_file

    def _export(self):
        to_export = {
            "version": 1
        }
        workouts = []

        count = 1

        if self._from_garmin_workouts_file:
            with open(self._from_garmin_workouts_file, 'r') as infile:
                garmin_workouts = json.load(infile)
                total_count = len(garmin_workouts)
                for garmin_workout in garmin_workouts:
                    try:
                        count_str = f"({count}/{total_count})"
                        count += 1
                        workout_parser = WorkoutParser(garmin_format=garmin_workout,
                                                       append_to_log=count_str)
                    except GarminConnectNotImplementedError as err:
                        to_export["error"] = "parsing error"
                        to_export["workouts"] = workouts
                        self.filename = "failed_workouts.yml"
                        self._write_to_stream(to_export)
                        raise err
                    own_format_workout = workout_parser.get_own_format()
                    workouts.append(own_format_workout)
        else:
            garmin_workouts_info = self.api_client.\
                get_workouts_info(self.limit, self.order_seq)
            total_count = len(garmin_workouts_info)

            for garmin_workout_info in garmin_workouts_info:
                try:
                    workout_info = WorkoutsInfoParser(garmin_workout_info)
                    if self._export_runs and workout_info.is_run():
                        garmin_workout = self.api_client.get_workout_details(
                            workout_info.get_id())

                        count_str = f"({count}/{total_count})"
                        count += 1
                        workout_parser = WorkoutParser(garmin_format=garmin_workout,
                                                        append_to_log=count_str)
                        own_format_workout = workout_parser.get_own_format()
                        workouts.append(own_format_workout)
                except GarminConnectNotImplementedError as err:
                    if err.property != "sportType.sportTypeKey":
                        # NOTE: Raise only different sports
                        raise err

                    count += 1
                    count_str = f"({count}/{total_count})"
                    log.info(f'Skipping {err.value} workout for now... {count_str}')

        to_export["workouts"] = workouts
        self._write_to_stream(to_export)

    def _write_to_stream(self, to_export):
        if self.stdout:
            print(yaml.dump(to_export, default_flow_style=False))
        else:
            with open(self.filename, 'w') as outfile:
                log.info('Storing workouts to the "%s"' % self.filename)
                yaml.dump(to_export, outfile)
