# -*- coding: utf-8 -*-
"""Setup views."""

# standard library imports

# third-party imports
from flask import Blueprint, render_template, abort, current_app
from flask_login import current_user

# application imports
from emol.utility.setup import test_encryption_key, is_setup

BLUEPRINT = Blueprint('setup', __name__)


@BLUEPRINT.before_request
def restrict_to_system_admin():
    """Intercept all requests to this blueprint before serving.

    If the eMoL instance is not set up, let things keep going.
    If it is set up and the user is not a system admin, plead ignorance.

    """
    if is_setup() is False:
        return

    if current_user.is_anonymous or current_user.is_system_admin is False:
        abort(404)


@BLUEPRINT.route('/setup', methods=['GET'])
def setup():
    """System setup view.

    See restrict_to_system_admin above for extra access controls.

    Returns:
        Rendered setup view

    """
    key_results = test_encryption_key(
        current_app.config.get('KEYFILE_PATH'))

    # Do we show the next button based on config test results
    next_ok = key_results.get('ok')

    return render_template(
        'admin/setup.html',
        db_exists = is_setup(),
        key_results=key_results.get('results'),
        db_user=current_app.config.get('DATABASE_USER'),
        db_database=current_app.config.get('DATABASE_DATABASE'),
        next_ok=next_ok
    )
