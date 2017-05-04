# -*- coding: utf-8 -*-
"""Initialize the database."""

# standard library imports
import traceback

# third-party imports
from flask import current_app, abort
from flask_sqlalchemy import SQLAlchemy


def init_database():
    """Bind the database."""
    current_app.logger.info('Initialize database')
    current_app.db = db = SQLAlchemy(current_app)
