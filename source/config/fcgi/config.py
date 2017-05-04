"""eMoL configuration file."""

# standard library imports
import os

# third-party imports
from authomatic.providers import oauth2

# application imports
# hahaha. no.

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(ROOT_DIR, 'db')

# Turn this off for production deployment!
DEBUG = True

DB_PATH = os.path.join(DB_DIR, 'emol.db')
IS_SETUP = os.path.exists(DB_PATH)

# Secret key for flask_login sessions. Make it something long and complex.
SECRET_KEY = '12345'

# Salt for calculating hashes. Make it something long and complex.
HASH_SALT = '12345'

# Location of your encryption key
KEYFILE_PATH = '/var/www/emol/.key/encrypt.key'

# Database credentials and configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////{dbpath}'.format(dbpath=DB_PATH)

# We don't need this, nor do we need the incessant warning about it
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Mail configuration
MAIL_HOST = 'localhost'
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = 'Ealdormere eMoL <emol@azureandor.ca>'
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

