# -*- coding: utf-8 -*-
"""API endpoint for cron-initiated requests.

Authorized external sources (cron) will invoke this endpoint with a validation
token and a task name to provide scheduled tasks.

The validation token lives in a filepath defined in the application config.
When cron intends to invoke this endpoint, it will read the cron token file and
use that as part of the URI being invoked. The endpoint attached to the URI will
verify the token for allow/deny.

When a cron request is done, the handler should call cron_helper.new_cron_token

"""

# standard library imports

# third-party imports
from flask import request, abort, current_app
from flask_restful import Resource

# application imports
from emol.cron.daily_check import daily_check


@current_app.api.route('/api/cron/<cron_token>/<task_name>')
class CronApi(Resource):
    """Endpoint for cron-invoked tasks.

    Permitted methods: POST

    This is a generic endpoint for cron-invoked tasks. Functionality should be
    placed in the emol.cron namespace and invoked from this class' POST
    handler.

    """

    @staticmethod
    def post(cron_token, task_name):
        """Run the task specified by task_name.

        Only requests from the localhost will be permitted, and only if the
        cron_token is correct.

        Arguments:
            cron_token: Validation token for authorization to invoke this api
            task_name: Name of the task to run

        """
        # Not invoked by localhost (i.e. cron)
        current_app.logger.info('cron request from {0.remote_addr}'.format(request))
        if request.remote_addr not in ['localhost', '127.0.0.1']:
            abort(403)

        # Wrong cron token
        if current_app.cron_helper.check_cron_token(cron_token) is False:
            abort(401)

        if task_name == 'daily_check':
            # Daily check for expiry reminders
            daily_check()
        elif task_name == 'unit_test':
            # For unit testing, NOP and get a new cron token
            pass
        else:
            # Invalid task name
            abort(403)

        # Get a new cron token
        current_app.cron_helper.new_cron_token()
