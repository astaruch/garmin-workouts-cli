import argparse
import logging
import sys

from login import Login

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stderr)
log.addHandler(console_handler)


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='garmin-workouts')

    def init_parser(self):
        subparsers = self.parser.add_subparsers(dest='command')

        login_parser = subparsers.add_parser(
            'login', help='Log in to the Garmin Connect')
        login_parser.add_argument(
            '-u', '--username', dest='username')
        login_parser.add_argument(
            '-p', '--password', dest='password')

        logout_parser = subparsers.add_parser(
            'logout', help='Log out from the Garmin Connect')

        export_parser = subparsers.add_parser(
            'export', help='Export all workouts')
        export_parser.add_argument(
            '--type', type=str, choices=['json', 'yaml'], dest='export_type')

        args = self.parser.parse_args()

        if args.command == 'login':
            login = Login(args.username, args.password)
            login.login()
        elif args.command == 'logout':
            print('Logging out...')
        elif args.command == 'export':
            print('Exporting data...')
