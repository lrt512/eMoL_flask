# -*- coding: utf-8 -*-
"""A faux user for the purposes of user self-service."""

from flask import current_app
from flask_login import AnonymousUserMixin


class FauxUser(AnonymousUserMixin):
    """A proxy for the User class.

    This is specifically for allowing combatants to update their own
    information via self-service. This class never sees or touches the database;
    it only exists to allow the combatant_update_info view to display the
    correct fields for a user updating their info.

    Attributes:
        id: Proxy for the PK field
        email: Proxy for the user email address
        system_admin: Proxy for the system admin flag

    """

    id = 0
    email = 'combatant_update@ealdormere.ca'
    system_admin = False

    @staticmethod
    def has_role(discipline, role):
        """Proxy User.has_role.

        Check if the user has the given role

        Args:
            discipline: The discipline to check against (None for global)
            role: The role keyword to check

        Returns:
            Boolean

        """
        # Under no circumstances is FauxUser allowed
        # to change anything to do with a discipline
        if discipline is not None:
            return False

        # And only one permitted global role
        return role in ['edit_combatant_info']

    def has_role_or(self, discipline, roles):
        """Proxy User.has_role_or.

        Check if the user has one of the given roles

        Args:
            discipline: The discipline to check against (None for global)
            roles: tuple of roles

        Returns:
            Boolean

        """
        for role in roles:
            if self.has_role(discipline, role):
                return True

        return False


class FauxUserSwitch(object):
    """Context manager to swap the FauxUser in and out.

    For self-serve combatant info updates.
    On entry, loads up the FauxUser as the current user.
    On exit, reloads the anonymous user.

    """
    def __enter__(self):
        user = FauxUser()
        current_app.login_manager.reload_user(user)

    def __exit__(self, exc_type, exc_val, exc_tb):
        current_app.login_manager.reload_user(None)
