import argparse
import logging
import sys
import http
import requests
import os
import re

from appdirs import AppDirs

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stderr)
log.addHandler(console_handler)

APP_NAME = 'garmin-workouts-cli'

package_dirs = AppDirs(APP_NAME)
if not os.path.exists(package_dirs.user_config_dir):
    os.makedirs(package_dirs.user_config_dir)

cookie_jar_path = f'{package_dirs.user_config_dir}/cookie.txt'


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
            return self.login(args)
        elif args.command == 'logout':
            print('Logging out...')
        elif args.command == 'export':
            print('Exporting data...')

    def login(self, args):
        self.session = requests.Session()
        self.session.cookies = http.cookiejar.LWPCookieJar(cookie_jar_path)

        if os.path.isfile(cookie_jar_path):
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)

        response = self.session.get("https://connect.garmin.com/modern/settings", allow_redirects=False)
        if response.status_code != 200:
            self.authenticate(args.username, args.password)
        else:
            log.debug('Using stored cookies')
        log.info("Login successful")

    def authenticate(self, username, password):
        log.info("Login with your Garmin Connect account. If you don't "
                 "have Garmin Connect account, head over to "
                 "https://connect.garmin.com/signin to create one.")
        if not username:
            username = input('Username: ')
        if not password:
            password = input('Password: ')

        form_data = {
            "username": username,
            "password": password,
            "embed": "false"
        }

        request_params = {
            "service": "https://connect.garmin.com/modern"
        }

        headers = {
            'origin': 'https://sso.garmin.com'
        }

        auth_response = self.session.post(
            url="https://sso.garmin.com/sso/signin",
            headers=headers,
            params=request_params,
            data=form_data)

        auth_response.raise_for_status()

        auth_ticket_url = self.extract_auth_ticket_url(auth_response.text)

        response = self.session.get(auth_ticket_url)
        response.raise_for_status()

        self.session.cookies.save(ignore_discard=True, ignore_expires=True)
        self.session.close()

    @staticmethod
    def extract_auth_ticket_url(auth_response):
        match = re.search(r'response_url\s*=\s*"(https:[^"]+)"', auth_response)
        if not match:
            raise Exception("Unable to extract auth ticket URL from:\n%s" % auth_response)
        auth_ticket_url = match.group(1).replace("\\", "")
        return auth_ticket_url
