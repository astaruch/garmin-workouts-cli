import requests
import http
import os
import re
import logging
import configparser

from appdirs import AppDirs


APP_NAME = 'garmin-workouts-cli'

package_dirs = AppDirs(APP_NAME)
if not os.path.exists(package_dirs.user_config_dir):
    os.makedirs(package_dirs.user_config_dir)

cookie_jar_path = f'{package_dirs.user_config_dir}/cookie.txt'

log = logging.getLogger(__name__)


class Login():
    def __init__(self, args={}):
        self.username = args.username if 'username' in args else None
        self.password = args.password if 'password' in args else None
        self.config_path = os.path.join(os.path.curdir, args.config) if \
            'config' in args else 'config.ini'
        self.cookie_jar_path = cookie_jar_path
        self.session = None

    def login(self):
        self.session = requests.Session()
        self.session.cookies = http.cookiejar.LWPCookieJar(cookie_jar_path)

        if os.path.isfile(cookie_jar_path):
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)

        response = self.session.get("https://connect.garmin.com/modern/settings", allow_redirects=False)
        if response.status_code != 200:
            self.authenticate(self.username, self.password)
            log.info('Login successful')
        else:
            log.debug('Using stored cookies')

    def authenticate(self, username, password):
        log.info("Login with your Garmin Connect account. If you don't "
                 "have Garmin Connect account, head over to "
                 "https://connect.garmin.com/signin to create one.")
        if self.config_path and os.path.exists(self.config_path):
            config = configparser.ConfigParser()
            config.read_file(open(self.config_path))
            if 'auth' in config:
                auth = config['auth']
                if not username and 'username' in auth:
                    log.info('Loading username from %s' % self.config_path)
                    username = auth['username']
                if not password and 'password' in auth:
                    log.info('Loading password from %s' % self.config_path)
                    password = auth['password']

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

    def get_session(self):
        return self.session

    def logout(self):
        if self.session:
            response = self.session.get('https://connect.garmin.com/modern/auth/logout')
            response.raise_for_status()
            self.session.cookies.clear()

        if os.path.exists(self.cookie_jar_path):
            os.remove(self.cookie_jar_path)

        log.info('Logged out')


    @staticmethod
    def extract_auth_ticket_url(auth_response):
        match = re.search(r'response_url\s*=\s*"(https:[^"]+)"', auth_response)
        if not match:
            raise Exception("Unable to extract auth ticket URL from:\n%s" % auth_response)
        auth_ticket_url = match.group(1).replace("\\", "")
        return auth_ticket_url
