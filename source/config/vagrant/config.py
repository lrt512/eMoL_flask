"""eMoL configuration file."""

# standard library imports
import os

# third-party imports
from authomatic.providers import oauth2

# application imports
# hahaha. no.

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Turn this off for production deployment!
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
KEYFILE_PATH = '/home/vagrant/.key/encrypt.key'
# We assume that 99% of the time you will be using the devserver
KEYFILE_OWNER = 'vagrant'

# Location for cron_token
CRON_TOKEN = '/home/vagrant/cron_token'

# Database credentials and configuration
SQLALCHEMY_DATABASE_URI = 'mysql://root:qwert@localhost/emol'

# We don't need this, nor do we need the incessant warning about it
SQLALCHEMY_TRACK_MODIFICATIONS = False

MAIL_DEFAULT_SENDER = 'Ealdormere eMoL <emol@ealdormere.ca>'

# Mail configuration for mailcatcher
MAIL_HOST = 'localhost'
MAIL_PORT = 1025
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_USE_SSL = False
MAIL_USE_TLS = False

del os

# OAUTH configuration for Authomatic
OAUTH2 = {
    'google': {
        'class_': oauth2.Google,
        'consumer_key': '362727061191-2aehro91hh3hkvqv4ro1oll8j0i63ujb.apps.googleusercontent.com',
        'consumer_secret': 'egAGDcIPcKwz7v3P6ZYF42Z0',
        'scope': oauth2.Google.user_info_scope
    }
}

