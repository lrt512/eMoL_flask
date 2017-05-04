# -*- coding: utf-8 -*-
"""Initialize application logger."""

# standard library imports

# third-party imports
from authomatic import Authomatic
from flask import current_app
from flask_login import LoginManager

# application imports
from emol.models import User, AnonymousUser
from emol.utility.setup import is_setup


def init_authentication():
    """Set up Authomatic and flask_login.

    see http://peterhudec.com/authomatic/

    """
    current_app.logger.info('Initialize authentication')
    current_app.authomatic = Authomatic(
        current_app.config.get('OAUTH2'),
        current_app.config.get('SECRET_KEY')
    )

    # Setup login manager
    current_app.login_manager = LoginManager()
    current_app.login_manager.init_app(current_app)
    current_app.login_manager.anonymous_user = AnonymousUser
    # Note that this is scoped within the init_authentication call so that
    # it is included in the with app.app_context: block in __init__.py
    # Otherwise this will raise a NameError as login_manager will be out of
    # scope

    # pylint hates callbacks
    # pylint: disable=unused-variable
    @current_app.login_manager.user_loader
    def load_user(user_id):
        """Map the user class for the flask_login manager."""
        current_app.logger.debug('login_manager: {}'.format(user_id))
        return User.query.filter(User.email == user_id).first()
