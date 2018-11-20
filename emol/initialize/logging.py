# -*- coding: utf-8 -*-
"""Initialize application logger."""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import current_app


def init_logging():
    """Set up a log file handler with rotation for the app."""
    file_handler = RotatingFileHandler(
        current_app.config.get(
            'LOG_FILE',
            os.path.join(current_app.instance_path, 'emol.log')
        ),
        maxBytes=current_app.config.get('LOG_MAX_SIZE', 1048576),
        backupCount=current_app.config.get('LOG_BACKUPS', 2),

    )
    formatter = logging.Formatter(
        current_app.config.get(
            'LOG_FORMAT',
            '%(asctime)-15s %(clientip)s %(message)s'
        )
    )

    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    current_app.logger.addHandler(file_handler)
    current_app.logger.info('Logging initialized')
