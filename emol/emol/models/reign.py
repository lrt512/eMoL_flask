# -*- coding: utf-8 -*-
"""Model for reign information."""

# standard library imports

# third-party imports
from flask import current_app as app

# application imports
from .discipline import Discipline
from .named_tuples import NameSlugTuple

__all__ = ['Reign']


class Reign(app.db.Model):
    """Model the infomation for a reign.

    This is used to track the various data for a reign. Used only for warrant
    rosters, currently.
    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    coronation = app.db.Column(app.db.Date, nullable=False)
    rex = app.db.Column(app.db.String(128), nullable=False)
    regina = app.db.Column(app.db.String(128), nullable=False)
    reign_title = app.db.Column(app.db.String(256), nullable=False)
