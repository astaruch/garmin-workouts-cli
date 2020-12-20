import argparse
import logging

from login import Login
from export import Export

log = logging.getLogger(__name__)


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='garmin-workouts')

    def init_parser(self):
        subparsers = self.parser.add_subparsers(dest='command')

        login_parser = subparsers.add_parser(
            'login', help='Log in to the Garmin Connect')
        login_parser.add_argument(
            '-u', '--username', dest='username',
            help='Username used in Garmin Connect')
        login_parser.add_argument(
            '-p', '--password', dest='password',
            help='Password for the account')
        login_parser.add_argument(
            '-c', '--config', dest='config', default='config.ini',
            help='Path to the config file. Check documentation to see possible sections.'
        )

        subparsers.add_parser(
            'logout', help='Log out from the Garmin Connect')

        export_parser = subparsers.add_parser(
            'export', help='Export workouts from the Garmin Connect')
        export_parser.add_argument(
            '-t', '--type', type=str, choices=['json', 'yaml', 'raw'],
            dest='export_type')

        args = self.parser.parse_args()

        if args.command == 'login':
            login = Login(args)
            login.login()
        elif args.command == 'logout':
            login = Login()
            login.logout()
        elif args.command == 'export':
            export = Export(args)
            export.export()
