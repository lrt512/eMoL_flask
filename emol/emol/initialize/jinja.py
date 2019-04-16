# -*- coding: utf-8 -*-
"""Jinja environment initialization."""

# standard library imports
import math

# third-party imports
import jinja2
from flask import current_app
from flask_login import current_user

# application imports


def init_jinja():
    """Register custom functions and filters with Jinja."""
    current_app.logger.info('Initialize Jinja')

    def check_authorization(auths, authorization):
        """Check if a combatant has an authorization.

        Return the boolean status of an authorization in the authorization data
        for a given discipline, in the format.
        {
            'authorization-a': True,
            'authorization-b': False,
            ...
        }

        The authorization data is simply the dict stored in
        Combatant.authorizations for a particular discipline.

        This is purely a convenience function for Jinja templates.

        Args:
            auths: Dict of combatant's authorizations for a discipline
            authorization: Slug for an authorization

        """
        if auths is None:
            return False

        return auths.get(authorization)

    def check_role(discipline, role, user=None):
        """Check if the current user has a role.

        Proxy User.has_role so that Jinja can return the selected property
        for a tag.

        Args:
            discipline: The discipline to check against (or 'global')
            role: The role to check for
            user: The user to check for, or current_user if None

        Returns:
            Boolean

        """
        user = user or current_user
        if user is None:
            return False

        if isinstance(role, tuple):
            return user.has_role_or(discipline, role)
        else:
            return user.has_role(discipline, role)

    jinja_globals = current_app.jinja_env.globals

    # Exports to Jinja globals

    def yes_no_auth(card, authorization):
        """Return HTML for yes or no values.

        A green FontAwesome checkmark or a red FontAwesome
        X depending on the result of check_authorization

        """
        if card.has_authorization(authorization):
            return '<i class="fa fa-check fa-lg green yes-no-icon"></i>'

        return '<i class="fa fa-close fa-lg red yes-no-icon"></i>'

    def yes_no_warrant(card, marshal):
        """Return HTML for yes or no values.

        A green FontAwesome checkmark or a red FontAwesome
        X depending on the result of check_authorization

        """
        if card.has_warrant(marshal):
            return '<i class="fa fa-check fa-lg green yes-no-icon"></i>'

        return '<i class="fa fa-close fa-lg red yes-no-icon"></i>'

    jinja_globals['yes_no_auth'] = yes_no_auth
    jinja_globals['yes_no_warrant'] = yes_no_warrant

    # Return selected attribute if the combatant has the authorization
    jinja_globals['has_auth'] = lambda card, auth: \
        'selected' if card is not None and card.has_authorization(auth) else ''

    # Return selected attribute if the combatant has the warrant
    jinja_globals['has_warrant'] = lambda card, marshal: \
        'selected' if card is not None and card.has_warrant(marshal) else ''

    # Return Pythonic boolean if the user has role.
    jinja_globals['has_role'] = check_role

    # Return HTML attribute selected of the user has the role.
    jinja_globals['has_role_select'] = lambda discipline, role, user=None: \
        'selected' if check_role(discipline, role, user) else ''

    # Return HTML attribute readonly of the user does not have the role
    jinja_globals['has_role_readonly'] = lambda discipline, role, user=None: \
        '' if check_role(discipline, role, user) else 'readonly'

    # Return HTML attribute disabled of the user does not have the role
    jinja_globals['has_role_disabled'] = lambda discipline, role, user=None: \
        '' if check_role(discipline, role, user) else 'disabled'

    # Return jQuery validate attribute required of the has the role
    jinja_globals['has_role_required'] = lambda discipline, role, user=None: \
        'required' if check_role(discipline, role, user) else ''

    # format a phone number 1234567890 as (123) 456-7890
    jinja_globals['phone'] = lambda x: '(%s) %s-%s' % (x[:3], x[3:6], x[-4:])

    jinja_globals['row_count'] = lambda x, y: int(math.ceil(x / (y * 1.0)))

    @current_app.template_filter('green')
    def green(text):
        # pylint will complain, but this is a callback
        # pylint: disable=unused-variable
        """Surround the text in a span to make it green."""
        return jinja2.Markup('<span class="fg-green">{0}</span>'.format(text))

    @current_app.template_filter('red')
    def red(text):
        # pylint will complain, but this is a callback
        # pylint: disable=unused-variable
        """Surround the text in a span to make it red."""
        return jinja2.Markup('<span class="fg-red">{0}</span>'.format(text))
