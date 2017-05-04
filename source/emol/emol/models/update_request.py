# -*- coding: utf-8 -*-
"""User request for information update."""

# standard library imports
import uuid
from datetime import datetime, timedelta

# third-party imports
from flask import url_for, current_app as app

# application imports
from emol.utility.database import default_uuid

__all__ = ['CombatantInfoUpdateRequest']


class UpdateRequest(app.db.Model):
    """Model a request combatant info update.

    When a combatant requests self-serve info update, one of these is generated.
    The request contains a unique token and is given an expiry date. When the
    user clicks the link in the email that is sent, they are shown the self-
    serve subset of the combatant info form that a User would see when editing.
    When the combatant submits the form, the combatant's info is updated in the
    database and the consumed date is set for the request.

    When a combatant attempts to update their info, the valid method should be
    invoked to ensure that the request has not expired and has not been
    consumed.

    The time to expire is 1 day by default and may be overridden in config using
    UPDATE_REQUEST_EXPIRY with an integer given in days.

    Attributes
        id: Primary key in the database
        token: The one-time

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    token = app.db.Column(app.db.String(36), unique=True, default=default_uuid)
    combatant_id = app.db.Column(app.db.Integer, app.db.ForeignKey('combatant.id'))
    combatant = app.db.relationship('Combatant')
    expiry = app.db.Column(app.db.DateTime)
    consumed = app.db.Column(app.db.DateTime)
    # TODO: Add IP address the update was made from

    def __init__(self, combatant):
        """Constructor.

        Set the expiry as either 1 day or the value of
        config.UPDATE_REQUEST_EXPIRY

        Args:
            combatant: A combatant

        """
        super().__init__(
            combatant=combatant,
            expiry=datetime.utcnow() + timedelta(days=1)
        )

    @classmethod
    def get_from_token(cls, token):
        """Get an update request by its token."""
        return cls.query.filter(cls.token == token).one()

    @classmethod
    def purge(cls, days):
        """Purge old update requests.

         TODO: Figure out if we should actually use this or remove. Might
                be a good idea to never lose the record of self-serve updates.

        Args:
            days: Number of days worth of info update requests to keep

        Returns:
            A UserInfoUpdateRequest or None
        """
        date = datetime.utcnow() + timedelta(days=-days)
        old_requests = cls.query.filter(cls.expiry > date).all()
        old_requests.delete()

    @property
    def change_info_url(self):
        """Generate the change info URL for this token."""
        return url_for(
            'combatant.update_info',
            token=self.token,
            _external=True
        )

    @property
    def valid(self):
        """Check whether this request is valid."""
        if self.expiry < datetime.utcnow():
            return False

        if self.consumed is not None:
            return False

        return True
