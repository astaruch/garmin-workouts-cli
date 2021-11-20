import argparse
import logging


log = logging.getLogger(__name__)


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='garmin-workouts',
                                              add_help=False)

    def print_help(self):
        self.parser.print_help()

    def init_parser(self):
        # type: (None) -> argparse.ArgumentParser
        # Basic options
        options = self.parser.add_argument_group('Options')
        options.add_argument(
            "-v", "--verbose", action="count", default=0,
            help="Increase output verbosity ")
        options.add_argument(
            "-h", "--help", action='store_true',
            help="Show this help message and exit"
        )

        # Sub-commands
        subparsers = self.parser.add_subparsers(title='Commands',
                                                dest='command',
                                                metavar='COMMAND')

        login_parser = subparsers.add_parser(
            'login', help='Log in to the Garmin Connect')
        login_parser.add_argument(
            '-u', '--username', dest='username',
            help='Username used in Garmin Connect')
        login_parser.add_argument(
            '-p', '--password', dest='password',
            help='Password for the account')
        login_parser.add_argument(
            '-c', '--config', dest='config', default='config.ini', type=str,
            help='Path to the config file. Check documentation to see possible sections.'
        )

        subparsers.add_parser(
            'logout', help='Log out from the Garmin Connect')

        export_parser = subparsers.add_parser(
            'export', help='Export workouts from the Garmin Connect to the '
            'file')
        export_parser.add_argument(
            '--runs', help="Export runs",
            dest='export_runs', action='store_true'
        )
        export_parser.add_argument(
            '--sort', type=str, choices=['asc', 'desc'],
            dest='export_sort', help="Default: asc",
            default='asc'
        )
        export_parser.add_argument(
            '--limit', type=int, dest='export_limit',
            help="Limit maximum number of workout",
        )
        export_parser.add_argument(
            '--workout-id', type=int, dest='export_workout_id',
            help="Download the specific workout with a given ID",
        )
        export_parser.add_argument(
            '-f', '--file', type=str, help='write to a file, instead of STDOUT'
            '. Leave the argument and program will generate a one.',
            nargs='?', const='', dest='export_file', metavar='FILENAME'
        )
        export_parser.add_argument(
            '--stdout', help="Print workouts to STDOUT instead of file.",
            action='store_true', dest='export_stdout'
        )
        export_parser.add_argument(
            '--from-garmin-workouts-file', type=str, help='Instead of export '
            ' from Garmin Connect, load workouts from given file.',
            dest='export_garmin_workouts_file'
        )
        import_parser = subparsers.add_parser(
            'import', help='Import workouts to the Garmin Connect from a file')
        import_parser.add_argument(
            '-f', '--file', type=str, help='Path to the file containing '
            'workouts definition', dest='import_file')

        return self.parser.parse_args()
