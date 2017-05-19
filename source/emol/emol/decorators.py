# -*- coding: utf-8 -*-
"""Decorators for access control."""

# standard library imports
from functools import wraps

# third-party imports
from flask import redirect, url_for, abort, _request_ctx_stack, session
from flask_login import current_user

# application imports
# Application imports here probably cause import loops


def login_required(handler_method):
    """Require that a user be logged in.

    To use it, decorate your method like this::

        @login_required
        def get(self):
            ...

    """
    @wraps(handler_method)
    def check_login(*args, **kwargs):
        """Perform the check."""
        if current_user.is_anonymous:
            # Short-circuit anonymous API invocations
            if 'emol.api' in args[0].__module__:
                abort(401)

            return redirect(url_for('home.login'))

        return handler_method(*args, **kwargs)

    return check_login


def role_required(role):
    """Require that a user have a specific global role.

    To use it, decorate your method like this::

        @role_required('can_edit_combatant')
        def get(self):
            ...

    """
    def actual_decorator(handler_method):
        """Extra nested function before the wrap.

        Necessary so that the role parameter is available within scope

        """
        @wraps(handler_method)
        def check_role(*args, **kwargs):
            """Perform the check."""
            if current_user.is_anonymous:
                abort(401)

            if current_user.has_role(None, role) is False:
                abort(401)

            return handler_method(*args, **kwargs)

        return check_role
    return actual_decorator


def admin_required(handler_method):
    """Require that a user be an admin.

    To use it, decorate your method like this::

        @admin_required
        def get(self):
            ...

    """
    @wraps(handler_method)
    def check_admin(*args, **kwargs):
        """Perform the check."""
        if current_user.is_anonymous:
            return redirect(url_for('home.login'))

        if current_user.is_admin:
            return handler_method(*args, **kwargs)

        abort(401)

    return check_admin
