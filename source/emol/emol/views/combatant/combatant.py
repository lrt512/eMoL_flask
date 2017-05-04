# -*- coding: utf-8 -*-
"""Combatant self-serve views."""

# standard library imports
import uuid
from datetime import datetime

# third-party imports
from flask import Blueprint, render_template, current_app
from flask_login import current_user

# application imports
from emol.models import Combatant, Discipline, UpdateRequest
from emol.models.faux_user import FauxUserSwitch
from emol.utility.hash import Sha256

BLUEPRINT = Blueprint('combatant', __name__)


@BLUEPRINT.route('/card/<card_id>', methods=['GET'])
def view_card(card_id):
    """Handle requests to view a combatant's card.

    Args:
        card_id: A combatant card ID

    Returns:
        - The message view if the card ID is invalid
        - The combatant's card if the card ID is valid

    """
    combatant = Combatant.query.filter(Combatant.card_id == card_id).one_or_none()
    if combatant is None:
        return render_template(
            'message/message.html',
            message='Could not find the specified combatant'
        )

    return render_template(
        'combatant/card.html',
        success=True,
        disciplines=Discipline.query.all(),
        combatant=combatant
    )


@BLUEPRINT.route('/update/<token>', methods=['GET'])
def update_info(token):
    """Handle requests to consume a combatant update info request.

    Args:
        token: An info update request token

    Returns:
        - The message view if the token is invalid
        - The self-serve info update view if the token is valid

    """
    token_valid = True
    update_request = UpdateRequest.query.filter(UpdateRequest.token == token).one_or_none()

    if update_request is None:
        token_valid = False
    elif update_request.expiry < datetime.utcnow():
        token_valid = False
    elif update_request.consumed is not None:
        token_valid = False

    if False and token_valid is False:
        return render_template(
            'message/message.html',
            message='Invalid token provided'
        )

    # Use the FauxUserSwitch context manager to provide an
    # "authorized user" for Jinja environment
    with FauxUserSwitch():
        return render_template(
            'combatant/combatant_update_info.html',
            combatant=update_request.combatant,
            token=token,
            validation_token=Sha256.generate_hash(token),
            is_self_serve=True
        )
