import os
import configparser
import logging

log = logging.getLogger(__name__)

class Shutdown(Exception): pass

class Config:

    """
    Class for working with the configuration file
    """

    def __init__(self, filename):
        self.filename = filename
        if not os.path.isfile(filename):
            log.critical("'{}'' does not exist".format(filename))
            raise Shutdown()

        try:
            config = configparser.ConfigParser(interpolation=None)
            config.read(filename, encoding='utf-8')
        except Exception as e:
            log.critical(str(e))
            raise Shutdown()

        # ---------------------------------------------------- #
        # DO NOT EDIT THIS FILE DIRECTLY. EDIT THE CONFIG FILE #
        # ---------------------------------------------------- #

        # [Bot]
        self.token = config.get('Bot', 'Token', fallback=None)
        self.prefix = config.get('Bot', 'Prefix', fallback=None)
        self.status = config.get('Bot', 'Status', fallback=None)
        self.activity = config.get('Bot', 'Activity', fallback=0)
        self.osu = config.get('Bot', 'OsuAPI', fallback=None)
        self.pb = config.get('Bot', 'PushBulletToken', fallback=None)
        self.validate()

    def validate(self):
        """
        Checks configuration options for valid values
        """
        critical = False
        if not self.token:
            print('You must provide a token in the config.ini')
            critical = True
        if not self.status:
            print('No Status provided!')
        if not self.osu:
            print('No osu!api key provided!')
        if not self.pb:
            print('No Push Bullet Token provided!')
        if critical:
            raise Shutdown()
