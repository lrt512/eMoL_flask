# -*- coding: utf-8 -*-
"""Model roles for access control."""

# standard library imports

# third-party imports
from flask import current_app as app

# application imports
from .named_tuples import RoleTuple
from .discipline import Discipline

__all__ = ['Role']


class Role(app.db.Model):
    """Model a role.

    Roles are assigned to users to indicate what actions they are permitted
    to perform. The UserRole class represents an association table matching
    Users to Roles.

    Attributes:
        id: Primary key in the database
        name: Readable name for the discipline
        slug: A tokenized version of the name friendly to database and URL
        discipline_id: If not None, points to the discipline this role is for

        _user_roles: The set of UserRole records referencing this role

    Relationships:
        discipline: The Discipline associated with this role, if any

    """

    # All roles
    USER_ROLES = [
        {'name': 'Can view combatant info', 'slug': 'view_combatant_info'},
        {'name': 'Can edit combatant info', 'slug': 'edit_combatant_info'},
        {'name': 'Can edit waiver dates', 'slug': 'edit_waiver_date'},
        {'name': 'Can edit card dates', 'slug': 'edit_card_date'},
        {'name': 'Can edit authorizations', 'slug': 'edit_authorizations'},
        {'name': 'Can edit marshal status', 'slug': 'edit_marshal'},
        {'name': 'Can generate warrant roster', 'slug': 'warrant_roster'},
        {'name': 'Can import combatants', 'slug': 'can_import'},
        {'name': 'Can edit kingdom officers', 'slug': 'edit_officer_info'}
    ]

    # Roles associated with editing combatants.
    # Used by User.can_see_combatant_list
    COMBATANT_EDIT_ROLES = (
        'view_combatant_info',
        'edit_combatant_info',
        'edit_card_date',
        'edit_authorizations',
        'edit_marshal'
    )

    # These roles are always global
    GLOBAL_ROLES = ['view_combatant_info', 'edit_combatant_info', 'edit_waiver_date']

    id = app.db.Column(app.db.Integer, primary_key=True)
    slug = app.db.Column(app.db.String(255), nullable=False)
    name = app.db.Column(app.db.String(255), nullable=False)

    discipline_id = app.db.Column(app.db.Integer, app.db.ForeignKey('discipline.id'))
    discipline = app.db.relationship('Discipline')

    @classmethod
    def find(cls, role, discipline):
        """Look up a role.

        Args:
            role: A role slug (or maybe a Role object)
            discipline: A discipline slug (string) or id (int) or
                Discipline object

        Returns:
            Role object

        Raises:
            ValueError if discipline can't be determined

        """
        #  Null case
        if isinstance(role, Role):
            return role

        discipline = Discipline.find(discipline)

        if isinstance(role, str):
            return Role.query.filter(
                Role.discipline_id == discipline.id).filter(
                Role.slug == role).one()
        elif isinstance(role, int):
            return Role.query.filter(
                Role.discipline_id == discipline.id).filter(
                Role.id == role).one()
        else:
            raise ValueError('Can''t determine role')

    @classmethod
    def template_list(cls):
        """Get a list of role names and slugs for template use."""
        return [RoleTuple(slug=r.slug, name=r.name, discipline=r.discipline)
                for r in Role.query.all()]
