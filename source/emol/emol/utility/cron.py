# -*- coding: utf-8 -*-
"""cron helper class."""

# standard library imports
import os
from uuid import uuid4

# third-party imports
from flask import current_app

# application imports


class CronHelper(object):
    """The cron helper class.

    This class manages the cron token that is used by the cron API endpoint
    (see api/cron_api.py).

    """

    def __init__(self, app):
        """Constructor.

        Get the cron token's path from config and join with the filename.
        Store the cron token filepath

        """
        self.__token_filename = app.config.get('CRON_TOKEN')
        current_app.logger.debug('cron_token in {0}'.format(app.config.get('CRON_TOKEN')))

    def new_cron_token(self):
        """Create a new cron access token.

        Any script that cron invokes must read <token_dir>/cron_token and use
        the token in there for any scheduler calls as
        /api/scheduler/<cron_token>/<task_name>

        Any time a scheduler task is completed, the cron token will be
        changed via this method.

        """
        # TODO: handle exceptions
        with open(self.__token_filename, 'w') as file_handle:
            token = uuid4().hex
            current_app.logger.debug('New cron token: {0}'.format(token))
            file_handle.write(token)

    def check_cron_token(self, token):
        """Validate the cron token.

        Compare the given token against the current cron token contained on
        disk.

        Arguments:
            token: the token to compare

        Returns:
            True if the token matches
        """
        # TODO: handle exceptions
        with open(self.__token_filename, 'r') as file_handle:
            cron_token = file_handle.read()
            current_app.logger.debug(
                'cron token in: {0} vs real cron token {1}'
                    .format(token, cron_token)
            )
            return cron_token == token
