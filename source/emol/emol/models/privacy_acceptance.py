# -*- coding: utf-8 -*-
"""Model to record combatants' acceptance of the privacy policy."""

# standard library imports
# pylint complains about the uuid import but it is used for Required(uuid.UUID)
# pylint: disable=unused-import
import uuid
from datetime import datetime

# third-party imports
from flask import url_for, current_app as app

# application imports
from emol.mail import Emailer
from emol.utility.database import default_uuid

__all__ = ['PrivacyAcceptance']


class PrivacyAcceptance(app.db.Model):
    """Record indicating acceptance of the privacy policy.

    When a Combatant record is inserted into the database, the listener
    event creates a matching PrivacyAccepted record. Any combatant who has
    a PrivacyAccepted record that is not resolved cannot use the system
    until they accept the privacy policy

    When the combatant accepts the privacy policy, the PrivacyAccepted record
    is resolved by noting the datetime that the privacy policy was accepted

    If the combatant declines the privacy policy, the Combatant record and the
    related PrivacyAcceptance is deleted from the database and the MoL is
    informed

    Attributes:
        id: Identity PK for the table
        uuid: A reference to the record with no intrinsic meaning
        accepted: Date the combatant accepted the privacy policy
        combatant_id: ID of the related combatant
        combatant: ORM relationship to the Combatant identified by combatant_id

    """
    id = app.db.Column(app.db.Integer, primary_key=True)

    combatant_id = app.db.Column(app.db.Integer, app.db.ForeignKey('combatant.id'))
    combatant = app.db.relationship(
        'Combatant',
        backref=app.db.backref('privacy_acceptance', uselist=False)
    )

    uuid = app.db.Column(app.db.String(36), default=default_uuid)
    accepted = app.db.Column(app.db.DateTime)

    @classmethod
    def create(cls, combatant):
        """Generate a PrivacyAccepted record for a combatant.

        Generates and saves the PrivacyAccepted record, then sends out the
        email to prompt the combatant to visit eMoL and read (heh) and accept
         the privacy policy

        Attributes:
            combatant: A combatant

        """
        privacy_acceptance = cls(combatant=combatant)
        emailer = Emailer()
        emailer.send_privacy_policy_acceptance(privacy_acceptance)

    @property
    def privacy_policy_url(self):
        """Generate the URL for a user to visit to accept the privacy policy.

        Uses the uuid member to uniquely identify this privacy accepted record,
        and through it the combatant.

        Returns:
            String containing the URL

        """
        return url_for('privacy_policy.index', uuid=self.uuid, _external=True)

    def resolve(self, accepted):
        if accepted is True:
            # Combatant accepted the privacy policy. Note the time of
            # acceptance, generate their card_id and email them the
            # link to their card
            self.accepted = datetime.utcnow()
            self.combatant.generate_card_id()
            emailer = Emailer()
            emailer.send_card_request(self.combatant)
            app.logger.debug('Sent card request email to {0}'.format(
                self.combatant.email
            ))

            has_sca_name = self.combatant.sca_name is not None

            return {
                'accepted': True,
                'card_url': self.combatant.card_url,
                'has_sca_name': has_sca_name
            }
        else:
            # Combatant declined the privacy policy, delete the Combatant
            # record for them and notify the MoL
            combatant = self.combatant
            app.db.session.delete(self)
            app.db.session.delete(combatant)
            app.logger.info('Deleted combatant {0}'.format(
                self.combatant.email))
            # TODO: Notify the MoL
            app.db.session.commit()

            return {'accepted': False}
