"""Run eMoL in the Flask debug HTTP server."""
# -*- coding: utf-8 -*-
"""Application initialization.

Various housekeeping tasks to get the app set up. Commentary inline.

"""

import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .commands import setup, import_combatants


def create_app(test_config=None):
    # Instantiate the app and configure from config.py
    app = Flask(__name__, instance_relative_config=True)
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    config_path = os.path.join(app.instance_path, 'config.py')
    config_source = None
    if test_config is not None:
        config_source = 'Using provided config mapping'
        app.config.from_mapping(test_config)
    elif os.path.exists(config_path):
        config_source = 'Using {}'.format(config_path)
        app.config.from_pyfile('config.py')
    else:
        config_source = 'Using default config mapping'
        app.config.from_mapping(
            DEBUG=True,
            SECRET_KEY='123456',
            SQLALCHEMY_DATABASE_URI='mysql+pymysql://emol:qwert@localhost/emol',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            CRON_TOKEN=os.path.join(app.instance_path, 'cron_token'),
            LOG_FILE=os.path.join(app.instance_path, 'emol.log'),
            LOG_FORMAT='%(asctime)-15s %(message)s'
        )

    # Add custom Flask commands
    app.cli.add_command(setup)
    app.cli.add_command(import_combatants)

    # Make sure security headers are set on all responses.
    # This should definitely be in some security module or something.
    @app.after_request
    def security_headers(response):
        """Ensure security headers are set on all responses."""
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' cdnjs.cloudflare.com;"
        return response

    app.db = SQLAlchemy()
    app.migrate = Migrate()

    with app.app_context():
        # Now initialize all the things
        from .initialize.logging import init_logging
        init_logging()

        app.db.init_app(app)
        app.migrate.init_app(app, app.db)

        app.logger.info(config_source)

        app.logger.info('Initialize database')

        # init_api MUST be called before init_blueprints
        from .initialize.api import init_api
        init_api()

        from .initialize.blueprint import init_blueprints
        init_blueprints()

        from .initialize.authentication import init_authentication
        from .initialize.cron import init_cron
        from .initialize.errors import init_error_handlers
        from .initialize.encryption import init_encryption
        from .initialize.jinja import init_jinja

        init_authentication()
        init_encryption()
        init_jinja()
        init_cron()
        init_error_handlers()

        return app
