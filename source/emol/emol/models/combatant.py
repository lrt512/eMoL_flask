# -*- coding: utf-8 -*-
"""Combatant database model.

Combatants are the centerpiece of eMoL. A combatant is someone who has
authorizations in a discipline and needs an authorization card to show for them.

"""

# standard library imports
import logging
import re
from datetime import date, datetime
from collections import namedtuple

# third-party imports
from flask import url_for, current_app as app
from flask_login import current_user
from slugify import slugify

# application imports
from emol.decorators import role_required
from emol.exception.combatant import CombatantDoesNotExist
from emol.exception.privacy_acceptance import PrivacyPolicyNotAccepted
from emol.mail import Emailer
from emol.utility.database import default_uuid
from emol.utility.date import add_years, DATE_FORMAT, string_to_date
from emol.utility.hash import Sha256
from emol.utility.value_tools import is_blank

from .card import Card
from .discipline import Discipline
from .privacy_acceptance import PrivacyAcceptance
from .waiver import Waiver

__all__ = ['Combatant']


class Combatant(app.db.Model):
    """A combatant.

    Attributes:
        id: Identity PK for the table
        uuid: A reference to the record with no intrinsic meaning
        card_id: A slug-like identifier for URLs
        last_update: Timestamp for last update of this record
        email: The combatant's email address
        sca_name: The combatant's SCA name
        encrypted: Encrypted blob of the combatant's personal information

    Backrefs:
        privacy_acceptance: The combatant's PrivacyAcceptance record
        cards: The combatant's authorization cards
        waiver: The combatant's waiver on file

    Properties:
        decrypted:  Provides access to the combatant's decrypted
                    personal information through the encrypted attribute

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    uuid = app.db.Column(app.db.String(36), default=default_uuid, nullable=False)

    # Friendly identifier for the combatant (see get_card_id)
    card_id = app.db.Column(app.db.String(255))

    last_update = app.db.Column(app.db.DateTime)

    # Data columns that are not encrypted
    email = app.db.Column(app.db.String(255), unique=True)
    sca_name = app.db.Column(app.db.String(255))

    cards = app.db.relationship(
        'Card',
        cascade='all, delete-orphan'
    )
    waiver = app.db.relationship(
        'Waiver',
        cascade='all, delete-orphan',
        backref='combatant',
        uselist=False
    )

    # Data fields for creating combatants
    # Anything marked True is required
    _combatant_info = {
        'email': True,
        'sca_name': False,
        'legal_name': True,
        'phone': True,
        'address1': True,
        'address2': False,
        'city': True,
        'province': True,
        'postal_code': True,
        'dob': False,
        'member_expiry': False,
        'member_number': False
    }

    # If something is in _combatant_info but is not in _encrypt_info
    # then it had better have a column declaration above or you will
    # get an error updating combatants
    _encrypt_info = [
        'legal_name',
        'phone',
        'address1',
        'address2',
        'city',
        'province',
        'postal_code',
        'dob',
        'member_number',
        'member_expiry'
    ]

    # Personal data encrypted in the database, cleartext in memory
    encrypted = app.db.Column(app.db.Text)
    # Decrypted data after load
    _decrypted = None

    def __repr__(self):
        """Printable representation."""
        return '<Combatant {0.id}: {0.email} ({0.name})>'.format(self)

    @property
    def decrypted(self):
        """Accessor for encrypted data.

        Populate the _decrypted attribute with either a blank slate or actual
        decrypted data.

        Returns:
            The decrypted data dictionary

        """
        if self._decrypted is None:
            if self.encrypted is None:
                self._decrypted = {}
            else:
                self._decrypted = app.cipher().decrypt_json(self.encrypted)

        return self._decrypted

    def update_encrypted(self):
        """Encrypt the decrypted data.

        If the combatant's personal info has been decrypted, re-encrypt it to
        capture any changes.

        """
        self.last_update = datetime.now()

        if self.decrypted is not None:
            self.encrypted = app.cipher().encrypt_json(self.decrypted)
            self._decrypted = None

    # Get methods

    @classmethod
    def get_by_id(cls, combatant_id):
        """Get a combatant by ID.

        Args:
            combatant_id: Combatant ID

        Returns:
            A Combatant object

        Raises:
            CombatantDoesNotExist if no record is found

        """
        combatant = Combatant.query.filter(Combatant.id == combatant_id).one_or_none()
        if combatant is None:
            raise CombatantDoesNotExist(combatant_id)

        return combatant

    @classmethod
    def get_by_uuid(cls, combatant_uuid):
        """Get a combatant by UUID.

        Args:
            combatant_uuid: Combatant UUID

        Returns:
            A Combatant object

        Raises:
            CombatantDoesNotExist if no record is found

        """
        combatant = Combatant.query.filter(Combatant.uuid == combatant_uuid).one_or_none()
        if combatant is None:
            raise CombatantDoesNotExist(combatant_uuid)

        return combatant

    @classmethod
    def get_by_email(cls, email):
        """Get a combatant by email address.

        Args:
            email: A combatant's email address

        Returns:
            A Combatant object

        Raises:
            CombatantDoesNotExist if no record is found

        """
        combatant = Combatant.query.filter(Combatant.email == email).one_or_none()
        if combatant is None:
            raise CombatantDoesNotExist(email)

        return combatant

    @classmethod
    def get_by_card_id(cls, card_id):
        """Get a combatant by card ID.

        Args:
            card_id: A card ID

        Returns:
            A Combatant object

        Raises:
            CombatantDoesNotExist if no record is found

        """
        combatant = Combatant.query.filter(Combatant.card_id == card_id).one_or_none()
        if combatant is None:
            raise CombatantDoesNotExist(card_id)
        return combatant

    @classmethod
    def get_by_sca_name(cls, name):
        """Get a combatant by SCA name.

        Args:
            name: Combatant's SCA name

        Returns:
            A Combatant object

        Raises:
            CombatantDoesNotExist if no record is found

        """
        combatant = Combatant.query.filter(Combatant.sca_name == name).one_or_none()

        if combatant is None:
            raise CombatantDoesNotExist(name)

        return combatant

    @property
    def name(self):
        """Get a combatant's name.

        Return the SCA name if defined, otherwise the legal name

        Returns:
            A name

        """
        return self.sca_name or self.decrypted.get('legal_name')

    def generate_card_id(self):
        """Generate a unique card ID for the combatant.

        Slugify the combatant's SCA name if they have one. Ensure the slug is
        unique and save it. If the combatant has no SCA name, generate a slug
        from their hashed legal name

        Returns:
            The card ID string

        Raises:
            PrivacyPolicyNotAccepted if the combatant has not yet done so

        """
        if self.privacy_acceptance.accepted is None:
            app.logger.error(
                'Privacy policy not accepted by {0.email}, not generating card id'
                .format(self)
            )
            raise PrivacyPolicyNotAccepted

        hashed = Sha256.generate_hash(self.decrypted.get('legal_name'))
        count = 0

        self.card_id = ''

        if not self.sca_name:
            app.logger.debug('Hashing legal name for {0.email}'.format(self))
            # No SCA name, use a hash
            card_id = hashed[count:count+6]
        else:
            app.logger.debug('Slugifying SCA name for {0.email}'.format(self))
            card_id = slugify(self.sca_name)

        # Ensure uniqueness
        while not self.card_id:
            try:
                app.logger.debug('checking card id {0}'.format(card_id))
                combatant = Combatant.get_by_card_id(card_id)

                if combatant.uuid == self.uuid:
                    # Pretending you don't exist is usually not good
                    # but it's okay right now
                    raise CombatantDoesNotExist

                # No exception means we are colliding with someone else
                # For no SCA name, just slide down the hash
                # For SCA name, append the first four characters of the hash
                if self.sca_name is None:
                    count += 1
                    card_id = hashed[count:count+6]
                else:
                    card_id += '-' + hashed[count:count+4]
            except CombatantDoesNotExist:
                # Exception means no combatant matched on card ID
                # so the current card ID is good to go
                app.logger.debug('card id {0} is OK, using it'.format(card_id))
                self.card_id = card_id

        app.db.session.commit()
        return self.card_id

    def validate_data(self, data):
        """Make sure all required data is present or already set."""
        for key, value in self._combatant_info.items():
            if value is False:
                # Not a required value
                continue

            if data.get(key) is None and self.decrypted.get(key) is None:
                raise ValueError('Missing unset value {0}'.format(key))

    @classmethod
    @role_required('edit_combatant_info')
    def create(cls, data):
        """Create a combatant.

        Data included in _combatant_info will be updated if the user's roles
        allow. Everything else will be ignored.

        Args:
            data: A dictionary of combatant data

        """
        # Look up via original_email in case this is a case of
        # combatant email being changed
        email = data.get('email')
        try:
            combatant = cls.get_by_email(email)
            raise Exception('Combatant {0} already exists'.format(email))
        except CombatantDoesNotExist:
            logging.info('New combatant: %s', data.get('legal_name'))
            # Make sure all required fields are present
            for field, required in cls._combatant_info.items():
                if required and field not in data:
                    raise ValueError('Required field "{0}" missing'.format(field))

            combatant = cls(
                email=data.get('email'),
                encrypted=None
            )

            app.db.session.add(combatant)
            app.db.session.commit()
            return combatant.update(data, is_new=True)

    @role_required('edit_combatant_info')
    def update(self, data, is_new=False):
        """Create or update a combatant using a dict of data.

        Data included in _combatant_info will be updated if the user's roles
        allow. Everything else will be ignored.

        Args:
            data: A dictionary of combatant data
            is_new:  Combatant is being updated for the first time after creation

        """
        if current_user.has_role(None, 'edit_waiver_date'):
            date_str = data.get('waiver_date')
            if date_str is not None:
                if self.waiver is None:
                    self.waiver = Waiver.create(self)
                else:
                    self.waiver.renew(date_str)

        # Invoke update_info for updating data that can be done via self-serve
        self.update_info(data, is_new)

        self.update_encrypted()
        self.last_update = datetime.utcnow()
        app.db.session.commit()

        if is_new:
            # Invoke the create class method to generate the
            # record, send an email, etc.
            PrivacyAcceptance.create(self)

        return self

    # named tuple for return values from update_info
    UpdateInfoReturn = namedtuple('UpdateInfoReturn', ['sca_name', 'email'])

    def update_info(self, data, is_new=False):
        """Update combatant self-serve data properties.

        Code factored out of create_or_update so that when a combatant is
        performing self-serve information update, they cannot change anything
        other than the subset of data (Combatant._combatant_info) they are
        supposed to be able to

        Args:
            data: A dict of combatant data to update
            is_new: Boolean indicating if the combatant record is new or not

        """
        self.validate_data(data)

        # In case something changes
        original_sca_name = self.sca_name
        original_email = self.email

        # Do the updates
        for field, value in data.items():
            if field not in self._combatant_info:
                continue

            # Special cases
            if not is_blank(value):
                if field == 'phone':
                    value = re.sub(r'[^0-9]', '', data[field])
                elif field == 'dob':
                    # Don't let minors edit their own DOB
                    continue

            if field in self._encrypt_info:
                self.decrypted[field] = value
            else:
                setattr(self, field, value)

        self.update_encrypted()

        # Combatant changed SCA name
        name_changed = original_sca_name != self.sca_name
        if is_new is False and name_changed and self.accepted_privacy_policy:
            self.card_id = self.generate_card_id()
            emailer = Emailer()
            emailer.send_card_request(self)

        # Log change of email if that is happening
        if original_email != self.email:
            logging.info('changed email address from %s to %s',
                         original_email, self.email)

        # return value for CombatantUpdateApi caller
        return self.UpdateInfoReturn(
            sca_name=original_sca_name != self.sca_name,
            email=original_email != self.email
        )

    def get_card(self, discipline, create=False):
        discipline = Discipline.find(discipline)

        for card in self.cards:
            if card.discipline is discipline:
                return card

        if create is True:
            card = Card.create(self, discipline)
            return card

    @property
    def card_url(self):
        """Card URL for this combatant.

        Compute the URL for this combatant's card from the combatant.view_card
        route and the combatant's card_id

        Returns:
            The URL as a string

        Raises:
            PrivacyPolicyNotAccepted if the combatant has not yet done so

        """
        if self.privacy_acceptance.accepted is None:
            app.logger.error(
                'Attempt to get card URL for {0} (privacy not accepted)'
                .format(self.email)
            )
            raise PrivacyPolicyNotAccepted

        if self.card_id is None or len(self.card_id) == 0:
            app.logger.error(
                (
                    'Attempt to get card_id for {0} but '
                    'card ID has not been allocated'
                ).format(self.e)
            )
            raise Exception('no')

        return url_for('combatant.view_card',
                       card_id=self.card_id,
                       _external=True)

    @property
    def accepted_privacy_policy(self):
        """Check if the combatant accepted privacy policy."""
        if self.privacy_acceptance is None:
            return False

        if self.privacy_acceptance.accepted is not None:
            return True

        return False

    @property
    def one_line_address(self):
        """Format the combatant's address as a one-liner."""
        if not self.decrypted.get('address2'):
            return '{0}, {1}, {2}  {3}'.format(
                self.decrypted.get('address1'),
                self.decrypted.get('city'),
                self.decrypted.get('province'),
                self.decrypted.get('postal_code'),
            )
        else:
            return '{0} {1}, {2}, {3}  {4}'.format(
                self.decrypted.get('address1').strip(),
                self.decrypted.get('address2'),
                self.decrypted.get('city'),
                self.decrypted.get('province'),
                self.decrypted.get('postal_code'),
            )

    def has_authorizations(self, discipline):
        """Check combatant for any authorizations in a given discipline.

        Args:
            discipline: Slug for the discipline in question

        Returns:
            True or False

        """
        authorizations = self.authorizations.get(discipline)
        for authorization in Discipline.get(slug=discipline).authorizations:
            if authorizations.get(authorization.slug) is True:
                return True

        return False

    def membership_valid(self, on_date=None):
        """Check if the combatant's membership is valid.

        Check the combatant's membership info in the encrypted blob.
        If the membership info is empty, then no. Otherwise, based on the
        membership expiry date

        Args:
            on_date: Optional date to check against, otherwise use today

        Returns:
            Boolean

        """
        member_number = self.decrypted.get('member_number')
        member_expiry = self.decrypted.get('member_expiry')

        if member_number is None:
            return False

        if member_expiry is None:
            return False

        member_expiry_date = string_to_date(member_expiry)

        if on_date is None:
            return member_expiry_date >= date.today()
        else:
            return member_expiry_date >= on_date

    @property
    def waiver_expiry(self):
        if self.waiver is not None:
            return self.waiver.expiry_date

        return None