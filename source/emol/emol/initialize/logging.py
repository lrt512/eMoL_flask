# -*- coding: utf-8 -*-
"""Initialize application logger."""

# standard library imports
import logging
from logging.handlers import RotatingFileHandler

# third-party imports
from flask import current_app

# application imports


def init_logging():
    """Set up a log file handler with rotation for the app."""
    file_handler = RotatingFileHandler(
        current_app.config.get('LOG_FILE'),
        maxBytes=current_app.config.get('LOG_MAX_SIZE'),
        backupCount=current_app.config.get('LOG_BACKUPS'),

    )
    formatter = logging.Formatter(current_app.config.get('LOG_FORMAT'))

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    current_app.logger.addHandler(file_handler)
    current_app.logger.info('Logging initialized')
