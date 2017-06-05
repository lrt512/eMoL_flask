# -*- coding: utf-8 -*-
"""Application initialization.

Various housekeeping tasks to get the app set up. Commentary inline.

"""

# standard library imports
import os

# third-party imports
from flask import Flask


def create_app():
    # Instantiate the app and configure from config.py
    app = Flask(__name__)
    try:
        print('Try config from local config.py')
        app.config.from_object('emol.config')
    except RuntimeError:
        print('No local config.py, try EMOL_CONFIG environment variable')
        app.config.from_envvar('EMOL_CONFIG')

    # Set up an app context
    app_context = app.app_context()
    app_context.push()

    # PEP 8 hates this but the imports can't happen at the module level

    # Now initialize all the things
    from emol.initialize.logging import init_logging
    init_logging()

    from emol.initialize.database import init_database
    init_database()

    # init_api MUST be called before init_blueprints
    from emol.initialize.api import init_api
    init_api()

    from emol.initialize.blueprint import init_blueprints
    init_blueprints()

    from emol.initialize.authentication import init_authentication
    from emol.initialize.cron import init_cron
    from emol.initialize.errors import init_error_handlers
    from emol.initialize.encryption import init_encryption
    from emol.initialize.jinja import init_jinja

    init_authentication()
    init_encryption()
    init_jinja()
    init_cron()
    init_error_handlers()

    return app
