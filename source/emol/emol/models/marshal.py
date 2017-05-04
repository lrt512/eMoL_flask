# -*- coding: utf-8 -*-
"""Model for a discipline's marshal."""

# standard library imports

# third-party imports
from flask import current_app as app

# application imports
from .discipline import Discipline
from .named_tuples import NameSlugTuple

__all__ = ['Marshal']


class Marshal(app.db.Model):
    """Model a type of marshal for a discipline.

    Often just "Marshal", but some places have specific marshal types
    e.g. "Cut and Thrust Marshal"

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    slug = app.db.Column(app.db.String(64), nullable=False)
    name = app.db.Column(app.db.String(64), nullable=False)

    discipline_id = app.db.Column(app.db.Integer, app.db.ForeignKey('discipline.id'))
    discipline = app.db.relationship('Discipline')

    @classmethod
    def find(cls, discipline, marshal):
        """Look up an Marshal.

        Args:
            discipline: A discipline slug (string) or id (int) or
                Discipline object
            marshal: A marshal slug (string) or id (int)
                or Marshal object

        Returns:
            Marshal object

        Raises:
            ValueError if marshal can't be determined

        """
        #  Null case
        if isinstance(marshal, Marshal):
            return marshal

        discipline = Discipline.find(discipline)

        if isinstance(marshal, str):
            return Marshal.query.filter(
                Marshal.discipline_id == discipline.id).filter(
                Marshal.slug == marshal).one()
        elif isinstance(Marshal, int):
            return Marshal.query.filter(
                Marshal.discipline_id == discipline.id).filter(
                Marshal.id == marshal).one()
        else:
            raise ValueError('Can''t determine marshal')

    @classmethod
    def template_list(cls, discipline):
        """Get a list of marshal names and slugs for template use."""
        return [NameSlugTuple(slug=m.slug, name=m.name)
                for m in Marshal.query.all()
                if m.discipline.slug == discipline]
