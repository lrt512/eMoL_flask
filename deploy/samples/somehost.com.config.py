"""eMoL configuration file.

Copy this into the private directory and rename it to match
the YAML file used for deployment. For example:

private
    ealdormere.ca.yaml
    ealdormere.ca.config.py

Now edit the copy in private/ to set the config values

"""

# standard library imports
import os

# third-party imports
from authomatic.providers import oauth2

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# This should be False for production deployment
DEBUG = True

# Secret key for flask_login sessions. Make it something long and complex.
SECRET_KEY = '12345'

# Salt for calculating hashes. Make it something long and complex.
HASH_SALT = '12345'

# Logging setup

LOG_FILE = '/tmp/emol.log'
LOG_MAX_SIZE = 100000
LOG_BACKUPS = 3
LOG_FORMAT = '%(asctime)-15s %(levelname)s: %(message)s'

# Location of your encryption key
KEYFILE_PATH = '/home/emol/.key/encrypt.key'
KEYFILE_OWNER = 'emol'

# Location for cron_token
CRON_TOKEN = '/home/emol/cron_token'

# Database credentials and configuration
SQLALCHEMY_DATABASE_URI = 'mysql://emol:sekritpassword@localhost/emol'

# We don't need this, nor do we need the incessant warning about it
SQLALCHEMY_TRACK_MODIFICATIONS = False

MAIL_DEFAULT_SENDER = 'Ealdormere eMoL <emol@ealdormere.ca>'

# Mail configuration
MAIL_HOST = 'localhost'
MAIL_PORT = 1025
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_USE_SSL = False
MAIL_USE_TLS = False

# OAUTH configuration for Authomatic
OAUTH2 = {
    'google': {
        'class_': oauth2.Google,
        'consumer_key': '<generated consumer key here>',
        'consumer_secret': '<generated consumer secret here>',
        'scope': oauth2.Google.user_info_scope
    }
}

