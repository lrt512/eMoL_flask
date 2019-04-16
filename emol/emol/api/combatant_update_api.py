# -*- coding: utf-8 -*-
"""API endpoint for combatant self-serve update.

This module implements the REST API endpoint allowing combatants to manage their
own information in a self-serve manner

Currently included are:

CombatantUpdateApi: Invoked update the combatant record


Combatants are permitted to update a select set of their information themselves.
The set currently includes:

    SCA name
    Email address
    Address1
    Address2
    City
    Province
    Postal Code
    Phone

Combatant info updates are authenticated via one-time token. When a combatant
requests an info update (see views/home.py), a CombatantInfoUpdateRequest
record is created (see models/update_request.py).

The created record has a generated token that is included in a URL sent to the
combatant in the change info request email. When the combatant visits the URL,
the token is validated as not expired and not already consumed
(see views/combatant/combatant.py) then the self-serve info update view is
shown for the user. The token is transformed into a validation token for the
transaction (simply so the request token is not reused verbatim).

When the updated info is submitted to the endpoint (this file), the validation
token is verified and if all is well, the combatant's information is updated.

Note that the Combatant model (models/combatant.py) has a specific method for
the self-serve update, Combatant.update_info, which is called by this and by
Combatant.create_or_update. The update_info method only touches the above-named
set, and so we have no possibility of a combatant changing any of their
properties beyond that set.

"""

# standard library imports
from datetime import datetime

# third-party imports
from flask import request, current_app
from flask_restful import Resource

# application imports
from emol.exception.combatant import CombatantDoesNotExist
from emol.models import UpdateRequest
from emol.models.faux_user import FauxUserSwitch


@current_app.api.route('/api/combatant_update')
class CombatantUpdateApi(Resource):
    """Endpoint for combatant self-serve info update.

    Permitted methods: PUT

    """

    @staticmethod
    def put():
        """Combatant self-serve info update.

        Validate the incoming validation token and then delegate incoming
        combatant data to the Combatant model class for update.

        If the combatant changed their SCA name, indicate that their card URL
        has changed and send an email to that effect.

        Returns:
            200 always. All messages, error or otherwise, are returned in the
            response JSON in the messages property
        """
        messages = []

        token = request.json.get('token')
        validate_token = request.json.get('validation_token')

        update_request = UpdateRequest.query.filter(
            UpdateRequest.token == token).one_or_none()

        if update_request is None or update_request.valid is False:
            messages.append('Unauthorized')
            return {'messages': messages}, 401

        try:
            # Update combatant info and re-encrypt personal info for save
            # Use the FauxUserSwitch context manager to provide an
            # "authorized user" for the info update
            with FauxUserSwitch():
                update_result = update_request.combatant.update_info(request.json)

            # Expire the update info request
            update_request.consumed = datetime.utcnow()
            current_app.db.session.commit()

            messages.append('Your information changes have been saved')

            # If combatant changed their SCA name, send an email
            # with the new card URL
            if update_result.sca_name is True:
                messages.append(
                    'Changing your SCA name changes the URL for your card. '
                    'An email has been sent with the new URL'
                )
                messages.append(
                    'You can now access your authorization card here:'
                )
                messages.append(
                    '<a href="{url}">{url}</a>'.format(
                        url=update_request.combatant.card_url
                    )
                )

                return {'messages': messages}, 200
        except CombatantDoesNotExist:
            current_app.logger.exception(
                'Put for combatant update, but combatant somehow does not exist'
            )
            messages.append('Combatant does not exist, somehow'), 400
            return {'messages': messages}
