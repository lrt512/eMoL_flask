# -*- coding: utf-8 -*-
"""Anonymous user class."""

from flask_login import AnonymousUserMixin


class AnonymousUser(AnonymousUserMixin):
    """A class to model a 'User' for anonymous visitors to the site.

    Enforces non-access privilege to administrative functionality. Basically,
    if asked anything it says no.

    Attributes and properties as described for User.
    """

    @property
    def is_system_admin(self):
        """Indicate whether this user is a system admin or not."""
        return False

    @property
    def can_see_combatant_list(self):
        """Indicate whether this user may see the combatant list or not."""
        return False

    def get_id(self):
        """Get the user's ID (email address)."""
        return 'anonymous@ealdormere.ca'

    def roles_for(self, discipline):
        """List the user's roles for a discipline.

        Creates a list of discipline slugs for each of this user's roles
        for the given discipline

        Args:
            discipline: Discipline slug

        Returns:
            List of slugs

        """
        return []

    def role_objects_for(self, discipline):
        """List the user's roles for the given discipline.

        Creates a list of UserRole objects for each of this user's roles
        for the given discipline

        Args:
            discipline: Discipline slug

        Returns:
            List of UserRole objects

        """
        return []

    def has_role(self, discipline, role):
        """Check if the user has the given role.

        Args:
            discipline: The discipline to check against (None for global)
            role: The role keyword to check

        Returns:
            Boolean

        """
        return False

    def has_role_or(self, discipline, roles):
        """Check if the user has one of the given roles.

        Args:
            discipline: The discipline to check against (None for global)
            roles: tuple of roles

        Returns:
            Boolean

        """
        return False

    def remove_role(self, discipline, role):
        """Remove a user role from this user.

        Args:
            discipline: Slug for the discipline (None for global)
            role: Slug for the role

        """
        pass

    def add_role(self, discipline, role):
        """Add a role to this user.

        Args:
            discipline: Slug for the discipline (None for global)
            role: Slug for the role

        """
        pass
