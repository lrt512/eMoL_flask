# -*- coding: utf-8 -*-
"""Privacy policy-related views."""

# standard library imports

# third-party imports
from flask import Blueprint, render_template

# application imports
from emol.models import PrivacyAcceptance

BLUEPRINT = Blueprint('privacy_policy', __name__)


@BLUEPRINT.route('/privacy-policy', methods=['GET'])
@BLUEPRINT.route('/privacy-policy/<uuid>', methods=['GET'])
def index(uuid=None):
    """Index view for privacy policy.

    If the URL has a UUID, look up the PrivacyAcceptance record for it. If it
    doesn't exist, show an error. If it does exist, the Accept/Decline prompt
    will be shown.

    If there is no UUID, just show the privacy policy as an informational view.

    Args:
        uuid: Optional UUID for a PrivacyAcceptance record

    Returns:
        Rendered message template or rendered privacy policy template
    """
    if uuid is not None:
        privacy_acceptance = PrivacyAcceptance.query.filter(
            PrivacyAcceptance.uuid == uuid).one_or_none()

        if privacy_acceptance is None:
            return render_template(
                'message/message.html',
                message='Could not locate any record for that key'
            )

    return render_template(
        'privacy/privacy_policy.html',
        uuid=uuid
    )
