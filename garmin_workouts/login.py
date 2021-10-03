import configparser
import logging
import os

from libs.garmin_api_client import GarminApiClient

log = logging.getLogger(__name__)


class Login():
    def __init__(self, args={}):
        self.username = args.username if 'username' in args else None
        self.password = args.password if 'password' in args else None
        self.config_path = os.path.join(os.path.curdir, args.config) if \
            'config' in args else 'config.ini'

        if not self.username or not self.password:
            self._get_credentials()

        api_client = GarminApiClient(self.username, self.password)
        self.session = api_client.session

    def get_session(self):
        return self.session

    def _get_credentials(self):
        if os.path.exists(self.config_path):
            config = configparser.ConfigParser()
            config.read_file(open(self.config_path))
            if 'auth' in config:
                auth = config['auth']
                if not self.username and 'username' in auth:
                    log.info('Loading username from %s' % self.config_path)
                    self.username = auth['username']
                if not self.password and 'password' in auth:
                    log.info('Loading password from %s' % self.config_path)
                    self.password = auth['password']

        if not self.username:
            self.username = input('Username: ')
        if not self.password:
            self.username = input('Password: ')
