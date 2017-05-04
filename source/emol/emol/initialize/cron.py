# -*- coding: utf-8 -*-
"""Initialize cron."""

# standard library imports

# third-party imports
from flask import current_app

# application imports
from emol.utility.cron import CronHelper


def init_cron():
    """Create a cron helper for the app and update the token."""
    current_app.logger.info('Initialize cron')
    current_app.cron_helper = CronHelper(current_app)
    current_app.cron_helper.new_cron_token()
