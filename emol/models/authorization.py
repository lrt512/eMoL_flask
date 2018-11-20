# -*- coding: utf-8 -*-
"""Model for an authorization."""

# standard library imports

# third-party imports
from flask import current_app as app

# application imports
from .discipline import Discipline
from .named_tuples import NameSlugTuple

__all__ = ['Authorization']


class Authorization(app.db.Model):
    """Model an authorization for a discipline.

    Authorizations are referenced by the Card model through the
    CombatantAuthorization association model. See Card model docs for detail.

    Attributes:
        id: Primary key in the database
        slug: Slugified name for the authorization
        name: Full name of the authorization
        discipline_id: ID of the discipline this card is for
        is_primary: Authorization can be a primary authorization

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    slug = app.db.Column(app.db.String(255), nullable=False)
    name = app.db.Column(app.db.String(255), nullable=False)
    is_primary = app.db.Column(app.db.Boolean, nullable=False, default=False)

    discipline_id = app.db.Column(app.db.Integer, app.db.ForeignKey('discipline.id'))
    discipline = app.db.relationship('Discipline')

    def __repr__(self):
        """String representation."""
        return '<Authorization: {0}.{1}>'.format(self.discipline.slug,
                                                 self.slug)

    @classmethod
    def find(cls, discipline, authorization):
        """Look up an authorization.

        Args:
            discipline: A discipline slug (string) or id (int) or
                Discipline object
            authorization: An authorization slug (string) or id (int)
                or Authorization object

        Returns:
            Authorization object

        Raises:
            ValueError if discipline or authorization can't be determined

        """
        #  Null case
        if isinstance(authorization, Authorization):
            return authorization

        discipline = Discipline.find(discipline)

        if isinstance(authorization, str):
            return Authorization.query.filter(
                Authorization.discipline_id == discipline.id).filter(
                Authorization.slug == authorization).one()
        elif isinstance(authorization, int):
            return Authorization.query.filter(
                Authorization.discipline_id == discipline.id).filter(
                Authorization.id == authorization).one()
        else:
            raise ValueError('Can''t determine authorization')

    @classmethod
    def template_list(cls, discipline):
        """Get a list of authorization names and slugs for template use."""
        return [NameSlugTuple(slug=a.slug, name=a.name)
                for a in Authorization.query.all() if
                a.discipline.slug == discipline]
