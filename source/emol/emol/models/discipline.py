# -*- coding: utf-8 -*-
"""Model for a discipline"""

# standard library imports
from datetime import date

# third-party imports
from flask import current_app as app

# application imports
from .named_tuples import NameSlugTuple

__all__ = ['Discipline', 'Authorization', 'Marshal']


class Discipline(app.db.Model):
    """Model a discipline.

    This class is an identifier and carrier for authorizations, marshals, and
    optionally card and waiver dates.

    The structure of Disciplines, Authorizations, and Marshals mirrors the
    structure of Combatant.authorizations.

    Combatant
        |
        - Authorizations
        |  |
        |  - Armoured Combat (discipline)
        |  |     |
        |  |     - Weapon and Shield (authorization)
        |  |     |
        |  |     - Two Weapon (authorization)
        |  |
        |  - Rapier (discipline)
        |        |
        |        - Heavy Rapier (authorization)
        |        |
        |       - Cut & Thrust (authorization)
        |
        - Marshals
        |   |
        |   - Armoured Combat (discipline)
        |   |   |
        |   |   - Marshal (marshal)
        |   |
        |   - Rapier (discipline)
        |       |
        |       - Marshal (marshal)
        |       |
        |       - Cut & Thrust Marshal (marshal)
        |
        |
        |- Card Dates
        |   |
        |   - Either one global, or one per discipline (see Card)
        |
        - Waiver Dates
             |
             - Either one global, or one per discipline (see Waiver)

    In code:

    Combatant.authorizations = {
        'armoured-combat': {
            'authorizations': {
                'weapon-shield': True,
                'two-weapon': True,
                'great-weapon': False
            },
            'marshal': {
                'marshal': True
            },
            'card_date': <date> (if per-discipline)
            'waiver_date': <date> (if per-discipline)
        },
        'rapier': {
            'authorizations': {
                'heavy-rapier': True,
                'cut-thrust': True,
                'two-weapon': False,
            },
            'marshal': {
                'marshal': True,
                'cut-thrust-marshal': True
            },
            'card_date': <date> (if per-discipline)
            'waiver_date': <date> (if per-discipline)
        }
    }

    Attributes:
        id: Primary key in the database
        name: Readable name for the discipline
        slug: A tokenized version of the name friendly to database and URL
        authorizations: The set of Authorization records s for this discipline
        card_date:  The card date for this discipline. If it is global then the
                    card date will be set from the combatant info tab and the
                    same date populated for all disciplines. If not global, then
                    each discipline tab will have a card date input and each
                    discipline's card date will be distinct.
        waiver_date: The waiver date for this discipline. If it is global then
                     the waiver date will be set from the combatant info tab
                     and the same date populated for all disciplines. If not
                     global, then each discipline tab will have a waiver date
                     input and each discipline's waiver date will be distinct.
        marshals: The set of Marshal records for this discipline
        officers:   The Kingdom officer responsible for this discipline.
                    This should only ever be one.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    slug = app.db.Column(app.db.String(255), nullable=False)
    name = app.db.Column(app.db.String(255), nullable=False)

    authorizations = app.db.relationship('Authorization')
    marshals = app.db.relationship('Marshal')

    def __repr__(self):
        """String representation."""
        return '<Discipline: {0}>'.format(self.slug)

    @classmethod
    def find(cls, discipline):
        """Find a discipline."""
        if discipline is None:
            return None

        if isinstance(discipline, Discipline):
            return discipline
        elif isinstance(discipline, str):
            return Discipline.query.filter(
                Discipline.slug == discipline).one()
        elif isinstance(discipline, int):
            return Discipline.query.filter(
                Discipline.id == discipline).one()
        else:
            raise ValueError('Can''t determine discipline')

    @classmethod
    def id_from_slug(cls, slug):
        """Get a discipline's database ID from a slug.

        Args:
            slug: Slug for a discipline

        Returns:
            ID of the discipline in the database
        """
        discipline = cls.query.filter(cls.slug == slug).one_or_none()
        return None if discipline is None else discipline.id

    @classmethod
    def template_list(cls):
        """Get a list of discipline names and slugs for template use."""
        return [NameSlugTuple(slug=d.slug, name=d.name)
                for d in Discipline.query.all()]


