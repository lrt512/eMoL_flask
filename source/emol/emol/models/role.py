# -*- coding: utf-8 -*-
"""Model roles for access control."""

# standard library imports

# third-party imports
from flask import current_app as app

# application imports
from .named_tuples import RoleTuple

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
        is_global: Indicates whether this role is global or not

        _user_roles: The set of UserRole records referencing this role

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
        {'name': 'Can edit kingdom officers', 'slug': 'can_edit_officers'}
    ]

    # Roles associated with editing combatants.
    # Used by User.can_see_combatant_list
    COMBATANT_EDIT_ROLES = (
        'view_combatant_info',
        'edit_combatant_info',
        'edit_waiver_date',
        'edit_card_date',
        'edit_authorizations',
        'edit_marshal'
    )

    # Roles that may or may not be global
    MAYBE_GLOBAL_ROLES = ['edit_waiver_date', 'edit_card_date']

    # These roles are always global
    GLOBAL_ROLES = ['view_combatant_info', 'edit_combatant_info']

    id = app.db.Column(app.db.Integer, primary_key=True)
    slug = app.db.Column(app.db.String(255), nullable=False)
    name = app.db.Column(app.db.String(255), nullable=False)
    is_global = app.db.Column(app.db.Boolean, nullable=False, default=False)

    @classmethod
    def id_from_slug(cls, slug):
        """Get the database ID of a role object based on its slug."""
        role = cls.query.filter(cls.slug == slug).one()
        return role.id

    @classmethod
    def is_global_card_date(cls):
        """Indicate whether the edit_card_date role is global or not."""
        return cls.query.filter(cls.slug == 'edit_card_date').one().is_global

    @classmethod
    def is_global_waiver_date(cls):
        """Indicate whether the edit_waiver_date role is global or not."""
        return cls.query.filter(cls.slug == 'edit_waiver_date').one().is_global

    @classmethod
    def template_list(cls):
        """Get a list of role names and slugs for template use."""
        return [RoleTuple(slug=r.slug, name=r.name, is_global=r.is_global)
                for r in Role.query.all()]
