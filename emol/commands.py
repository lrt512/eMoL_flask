# Copyright (c) 2018 Some Entity. All Rights Reserved.

"""Click commands for the application."""

import os
from shutil import copyfile
import sys

import click
from flask import current_app
from flask.cli import with_appcontext


@click.command()
@with_appcontext
def initialize():
    """Initialize the application.

    - Create the database
    - Add a read-only user
    - Add a read-write user
    """
    from .database.initialize import initialize_db
    click.echo('Initializing application...')

    # Ensure the instance folder exists
    try:
        os.makedirs(current_app.instance_path)
    except OSError:
        pass

    copyfile(
        'config_example.py',
        os.path.join(current_app.instance_path, 'config.py')
    )

    try:
        initialize_database()
        initialize_db()
        seed_users()
    except RuntimeError as exc:
        click.echo(exc, err=True)
        click.echo('Aborting initialization', err=True)
        sys.exit(-1)

    click.echo('Initialization complete.')
    click.echo('Be sure to edit instance/config.py to set MEMCACHE_SERVER')
