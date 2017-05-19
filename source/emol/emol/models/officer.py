# -*- coding: utf-8 -*-
"""Officer database model."""

# standard library imports

# third-party imports
from flask import current_app as app
from sqlalchemy import inspect

# application imports
from .discipline import Discipline

__all__ = ['Officer']


class Officer(app.db.Model):
    """Model a kingdom officer.

    Officers are not necessarily users of the system, and users of the system
    are not necessarily officers, so Officer records are not linked to User
    records.

    Properties:
        id: Primary key in the database
        title: Long name of the officer title (e.g. Earl Marshal)
        short_title = Short name of the officer title (e.g. EM)

        legal_name: Officer's legal name
        sca_name: Officer's SCA name
        address1: Officer's address, first line
        address2: Officer's address, second line
        city: Officer's city
        state: Officer's state/province
        postal_code: Officer's postal code
        phone: Officer's phone number

        note: Note for officer (e.g. "No calls after 9PM, please")
        parent: Parent officer, if any
        discipline: Discipline this officer is associated with

    """

    id = app.db.Column(app.db.Integer, primary_key=True)

    # The office
    title = app.db.Column(app.db.String(255))
    short_title = app.db.Column(app.db.String(255))

    # The person
    legal_name = app.db.Column(app.db.String(255))
    sca_name = app.db.Column(app.db.String(255))
    email = app.db.Column(app.db.String(255))
    address1 = app.db.Column(app.db.String(255))
    address2 = app.db.Column(app.db.String(255))
    city = app.db.Column(app.db.String(255))
    state = app.db.Column(app.db.String(2))
    postal_code = app.db.Column(app.db.String(10))
    phone = app.db.Column(app.db.String(10))

    note = app.db.Column(app.db.String(1024))

    discipline_id = app.db.Column(app.db.Integer, app.db.ForeignKey('discipline.id'))
    discipline = app.db.relationship('Discipline')

    parent_id = app.db.Column(app.db.Integer, app.db.ForeignKey('officer.id'))
    parent = app.db.relationship('Officer', backref='children', remote_side=[id])

    allowed_empty = ['discipline_id', 'parent_id', 'address2', 'note']

    @classmethod
    def create_or_update(cls, data):
        """Update an officer, or create if nonexistent.

        Args:
            data: A dict of officer information

        """
        officer = Officer.query.filter(Officer.short_title == data.get('short_title')).one_or_none()
        if officer is None:
            officer = Officer()
            app.db.session.add(officer)

        for column in inspect(Officer).columns:
            key = column.key
            if key == 'id':
                continue

            value = data.get(column.key)

            if value is None:
                if key in cls.allowed_empty:
                    continue

                raise Exception(column)

            if key == 'discipline':
                if len(value) == 0:
                    officer.discipline = None
                else:
                    officer.discipline = Discipline.find(value)
            elif key == 'parent':
                if len(value) == 0:
                    officer.parent = None
                else:
                    parent = Officer.query.filter(Officer.short_title == value).one_or_none()
                    if parent != officer:
                        officer.parent = parent
            else:
                setattr(officer, key, value)

        app.db.session.commit()
        return officer
