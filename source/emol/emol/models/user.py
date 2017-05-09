# -*- coding: utf-8 -*-
"""User database model."""

# standard library imports

# third-party imports
from flask import current_app as app

# application imports
from .faux_user import FauxUser
from .discipline import Discipline
from .role import Role

__all__ = ['User', 'UserRole']


class User(app.db.Model):
    """Model a user.

    A user is a Google account that is permitted to actually log in to eMoL.
    The set of users is small, typically the Earl Marshal, their deputies, and
    any Ministers of the List.

    Users must map to a Google account through the email property.

    Properties:
        id: Primary key in the database
        email: User's email address for their Google account
        system_admin: Flag for users who have configuration privilege

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    email = app.db.Column(app.db.String(255), unique=True)
    system_admin = app.db.Column(app.db.Boolean, nullable=False, default=False)

    roles = app.db.relationship('UserRole')

    def __repr__(self):
        """String representation."""
        return '<User %r>' % self.email

    @property
    def is_active(self):
        """Check whether the user is active or not.

        Required by flask_login.

        We don't have the concept of disabled users at this time

        Returns:
            Boolean

        """
        return True

    @property
    def is_authenticated(self):
        """Check whether the user is authenticated or not.

        Required by flask_login.

        The fact that this User object exists means that you have been
        authenticated by Google

        Returns:
            Boolean

        """
        return True

    @property
    def is_anonymous(self):
        """Check whether the user is anonymous or not.

        Required by flask_login.

        Anonymous users don't get User objects

        Returns:
            Boolean

        """
        return False

    @property
    def is_admin(self):
        """Admin flag required by flask_login.

        Note that we use the admin role here, not the system_admin flag

        Returns:
            Boolean

        """
        return self.has_role(None, 'admin')

    @property
    def is_system_admin(self):
        """Indicate whether this user is a system admin or not."""
        return self.system_admin

    @property
    def can_see_combatant_list(self):
        """Indicate whether this user may see the combatant list or not."""
        # Ultimate cosmic power
        if self.system_admin is True:
            return True

        # roles really is an iterable
        # noinspection PyTypeChecker
        for role in self.roles:
            if role.role.slug in Role.COMBATANT_EDIT_ROLES:
                return True

        return False

    def get_id(self):
        """Get the user's ID (email address)."""
        return self.email

    def roles_for(self, discipline):
        """List the user's roles for a discipline.

        Creates a list of discipline slugs for each of this user's roles
        for the given discipline

        Args:
            discipline: Discipline slug

        Returns:
            List of slugs

        """
        discipline = Discipline.find(discipline)

        return [ur.role.slug for ur in self.roles
                if ur.discipline_is(discipline)]

    def role_objects_for(self, discipline):
        """List the user's roles for the given discipline.

        Creates a list of UserRole objects for each of this user's roles
        for the given discipline

        Args:
            discipline: Discipline slug

        Returns:
            List of UserRole objects

        """
        return [ur for ur in self.roles
                if ur.discipline_is(discipline)]

    def has_role(self, discipline, role):
        """Check if the user has the given role.

        Args:
            discipline: The discipline to check against (None for global)
            role: The role keyword to check

        Returns:
            Boolean

        """
        if len(self.roles) == 0:
            return False

        # Ultimate cosmic power
        if self.system_admin:
            return True

        discipline = Discipline.find(discipline)
        if role in self.roles_for(discipline):
            return True

        return False

    def has_role_or(self, discipline, roles):
        """Check if the user has one of the given roles.

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

    def remove_role(self, discipline, role):
        """Remove a user role from this user.

        Args:
            discipline: Slug for the discipline (None for global)
            role: Slug for the role

        """
        if self.has_role(discipline, role) is False:
            return

        discipline_roles = self.role_objects_for(discipline)
        for user_role in discipline_roles:
            if user_role.role.slug == role:
                user_role.delete()
                break

        app.db.session.commit()

    def add_role(self, discipline, role):
        """Add a role to this user.

        Args:
            discipline: Slug for the discipline (None for global)
            role: Slug for the role

        """
        if self.has_role(discipline, role):
            return

        print(discipline, role)

        user_role = UserRole(
            user=self,
            role=Role.query.filter(Role.slug == role).one(),
            discipline=Discipline.find(discipline) if discipline else None
        )

        app.db.session.add(user_role)
        app.db.session.commit()

    def add_roles(self, discipline, roles):
        """Add a role to this user.

        Args:
            discipline: Slug for the discipline (None for global)
            role: Slug for the role

        """
        for role in roles:
            self.add_role(discipline, role)

    @classmethod
    def combatant_update_user(cls):
        """Create a temporary user for user self-service.

        The user has edit_combatant_info role so that users can edit
        their own info. It is not connected to the database in any way
        and cannot be modified as a regular User object

        Returns:
            A FauxUser object

        """
        return FauxUser()


class UserRole(app.db.Model):
    """Model class for a role assigned to a user.

    This corresponds to an association table for (User, Role)

    Attributes:
        id: Primary key in the database
        user: A User object
        role: A Role object
        discipline: A Discipline object, or None if the role is global

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    user_id = app.db.Column(app.db.Integer, app.db.ForeignKey('user.id'))
    user = app.db.relationship('User')
    role_id = app.db.Column(app.db.Integer, app.db.ForeignKey('role.id'))
    role = app.db.relationship('Role')

    discipline_id = app.db.Column(app.db.Integer, app.db.ForeignKey('discipline.id'))
    discipline = app.db.relationship('Discipline')

    def __repr__(self):
        """String representation."""
        return '<UserRole: {0} => {1}.{2}'.format(
            self.user_id,
            "global" if self.discipline_id is None else self.discipline.slug,
            self.role.slug
        )

    def discipline_is(self, discipline):
        """Convenience function to check the role's discipline.

        Args:
            discipline: Discipline to check

        Returns: Boolean

        """
        if self.discipline is None:
            return discipline is None

        return (self.discipline.name == discipline or
                self.discipline.slug == discipline or
                self.discipline is discipline)
