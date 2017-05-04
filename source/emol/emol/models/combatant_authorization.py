# -*- coding: utf-8 -*-
"""Combatant authorization model."""

# standard library imports

# third-party imports
from flask import current_app as app

# application imports

__all__ = ['CombatantAuthorization']


class CombatantAuthorization(app.db.Model):
    """Link an authorization to a combatant's card.

    Properties:
        card_id: The card
        authorization_id: The authorization

    """
    __tablename__ = 'combatant_authorization'
    __table_args__ = (app.db.UniqueConstraint('card_id', 'authorization_id'),)

    card_id = app.db.Column(
        app.db.Integer,
        app.db.ForeignKey('card.id'),
        primary_key=True)

    authorization_id = app.db.Column(
        app.db.Integer,
        app.db.ForeignKey('authorization.id'),
        primary_key=True
    )
