# Copyright (c) 2018 Some Entity. All Rights Reserved.

"""Click commands for the application."""

import os
from csv import DictReader

from click import argument, command, File
from flask import current_app
from flask.cli import with_appcontext
from yaml import safe_load


@command()
@argument('config_yaml', type=File('r'))
@with_appcontext
def setup(config_yaml):
    """Initialize the application."""
    current_app.logger.info(
        'Setting up application from {}'
            .format(config_yaml.name)
    )

    # Ensure the instance folder exists
    try:
        os.makedirs(current_app.instance_path)
    except OSError:
        pass

    # Read YAML
    with current_app.app_context():
        from emol.setup import setup
        config = safe_load(config_yaml)
        setup(config)


@command()
@argument('combatant_file', type=File('r'))
@with_appcontext
def import_combatants(combatant_file):
    """Import some combatants"""
    from emol.models import Combatant, User
    from flask_login import login_user
    current_app.logger.info('Importing combatants'.format(combatant_file.name))

    user = User.query.filter(User.system_admin == 1).first()

    # Use a fake request context so we can log in the user
    with current_app.test_request_context():
        login_user(user)

        # Read CSV
        with current_app.app_context():
            csv = DictReader(combatant_file)
            for row in csv:
                Combatant.create(row)
