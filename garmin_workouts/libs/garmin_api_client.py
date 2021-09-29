import logging
import http
import os
import re
import requests
import json
from fake_useragent import UserAgent

from appdirs import AppDirs

APP_NAME = 'garmin-workouts-cli'

package_dirs = AppDirs(APP_NAME)
if not os.path.exists(package_dirs.user_config_dir):
    os.makedirs(package_dirs.user_config_dir)

cookie_jar_path = f'{package_dirs.user_config_dir}/cookie.txt'

log = logging.getLogger(__name__)


class GarminApiClient():
    """
    Class to comunicate with Garmin Connect API
    """
    def __init__(self, username=None, password=None, session=None):
        self.username = username
        self.password = password
        self.cookie_jar_path = cookie_jar_path
        self.session = session

        if not self.session:
            self.login()

    def login(self):
        self.session = requests.Session()
        self.session.cookies = http.cookiejar.LWPCookieJar(cookie_jar_path)

        if os.path.isfile(cookie_jar_path):
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)

        response = self.session.get("https://connect.garmin.com/modern/settings", allow_redirects=False)
        if response.status_code != 200:
            self._authenticate()
            log.info('Login successful')
        else:
            log.debug('Using stored cookies')

    def logout(self):
        if self.session:
            response = self.session.get('https://connect.garmin.com/modern/auth/logout')
            response.raise_for_status()
            self.session.cookies.clear()

        if os.path.exists(self.cookie_jar_path):
            os.remove(self.cookie_jar_path)

        log.info('Logged out')

    def get_workouts_info(self, limit, order_seq):
        # type: (int, str) -> object
        workouts_url = "https://connect.garmin.com/proxy/workout-service/workouts"
        workouts_params = {
            "start": 1,
            "limit": limit,
            "myWorkoutsOnly": True,
            "sharedWorkoutsOnly": False,
            "orderBy": "WORKOUT_NAME",
            "orderSeq": order_seq,
            "includeAtp": False,
        }
        workouts_response = self.session.get(
            url=workouts_url,
            params=workouts_params)
        workouts_response.raise_for_status()

        return json.loads(workouts_response.text)

    def get_workout_details(self, id):
        workout_url = f'https://connect.garmin.com/proxy/workout-service/workout/{id}'
        workout_response = self.session.get(workout_url)

        return json.loads(workout_response.text)

    def upload_new_workout(self, workout_json, workout_name):
        log.info(f"Uploading a new workout '{workout_name}' to the Garmin Connect")
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "NK": "NT",
            "Referer": "https://connect.garmin.com/modern/workouts",
            "Content-Type": "application/json",
        }
        response = self.session.post(
            "https://connect.garmin.com/modern/proxy/workout-service/workout",
            headers=headers, data=workout_json)
        response.raise_for_status()

        response_json = response.json()
        new_workout_url = f"https://connect.garmin.com/modern/workout/{response_json['workoutId']}"
        log.info(f'New workout created: {new_workout_url}')
        return response_json

    def _authenticate(self):
        username = self.username
        password = self.password
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
            "embed": "false",
            "rememberme": "on"
        }

        request_params = {
            "service": "https://connect.garmin.com/modern"
        }

        headers = {
            'origin': 'https://sso.garmin.com',
            'User-Agent': self._genenerate_user_agent()
        }

        auth_response = self.session.post(
            url="https://sso.garmin.com/sso/signin",
            headers=headers,
            params=request_params,
            data=form_data)

        auth_response.raise_for_status()

        auth_ticket_url = self._extract_auth_ticket_url(auth_response.text)

        response = self.session.get(auth_ticket_url)
        response.raise_for_status()

        self.session.cookies.save(ignore_discard=True, ignore_expires=True)
        self.session.close()

    def _genenerate_user_agent(self):
        ua = UserAgent()
        return ua.random

    def _extract_auth_ticket_url(self, auth_response):
        match = re.search(r'response_url\s*=\s*"(https:[^"]+)"', auth_response)
        if not match:
            raise Exception("Unable to extract auth ticket URL from:\n%s" % auth_response)
        auth_ticket_url = match.group(1).replace("\\", "")
        return auth_ticket_url
