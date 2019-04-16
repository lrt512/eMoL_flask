# -*- coding: utf-8 -*-
"""Privacy policy API endpoints.

This module implements REST API endpoints for combatants accepting or declining
the eMoL privacy policy

PrivacyPolicyApi: Invoked when a user accepts or declines the privacy policy

ResendPrivacyPolicyApi: Invoked to resend the privacy policy email to a
                        combatant

"""

# standard library imports
from datetime import datetime

# third-party imports
from flask import request, current_app
from flask_restful import Resource

# application imports
from emol.decorators import login_required
from emol.exception.combatant import CombatantDoesNotExist
from emol.mail import Emailer
from emol.models import Combatant, PrivacyAcceptance


@current_app.api.route('/api/privacy_policy')
class PrivacyPolicyApi(Resource):
    """Endpoint for privacy policy acceptance.

    Permitted methods: POST

    """

    @staticmethod
    def post():
        """Accept or decline the privacy policy.

        The request JSON property should have an object:
        {
            uuid: <uuid>,
            accepted: <boolean>
        }

        The UUID will be used to look up the PrivacyAcceptance which will have
        a reference to the combatant in question.

        if accepted is True, the acceptance is recorded, the combatant's card
        URL generated, and an email with the URL sent to the combatant's email
        address.

        If accepted is False, the combatant is deleted from the database.
        TODO: Also, email the MoL so they can track manually

        Returns:
            200 always.

            A JSON object is returned as the body:
            {
                accepted: True or False,
                card_url: <combatant's card URL>,   # if accepted is True
                has_sca_name: <boolean>             # else not present
            }
        """
        privacy_acceptance = PrivacyAcceptance.query.filter(
            PrivacyAcceptance.uuid == request.json['uuid']).one_or_none()

        if privacy_acceptance is None:
            return {'message': "We couldn't find a record for that key"}, 400

        accepted = request.json.get('accepted')
        return privacy_acceptance.resolve(accepted)


@current_app.api.route('/api/resend_privacy/<uuid>')
class ResendPrivacyPolicyApi(Resource):
    """Endpoint for resending the privacy policy email.

    Permitted methods: POST

    """

    @staticmethod
    @login_required
    def post(uuid):
        """Resend the privacy policy email for a combatant.

        Use the given UUID to look up the combatant, then create an emailer
        and trigger send of the privacy policy email.

        Args:
            uuid: The combatant's UUID

        Returns:
            200 always

            A JSON object is returned as the body:
            {
                message: <a response message>
            }
        """
        try:
            combatant = Combatant.get_by_uuid(uuid)
            if combatant.accepted_privacy_policy:
                return {
                    'message': 'Combatant has already accepted privacy policy'}

            emailer = Emailer()
            emailer.send_privacy_policy_acceptance(
                combatant.privacy_acceptance)
        except CombatantDoesNotExist:
            current_app.logger.exception(
                'No combatant with uuid {0} for resend privacy policy'
                .format(uuid)
            )
            return {'message': 'No combatant exists for that ID'}
