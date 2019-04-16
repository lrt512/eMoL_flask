"""Unit tests for combatant update API."""

import json
from uuid import uuid4

from emol.models import Combatant, UpdateRequest
from emol.utility.date import string_to_date


def test_update_bad_token(app, combatant):
    """Test user update API with bad token."""
    client = app.test_client()
    response = client.put(
        '/api/combatant_update',
        data=json.dumps({'token': uuid4().hex}),
        content_type = 'application/json'
    )

    assert response.status_code == 401


def test_update(app, combatant):
    """Test update on valid fields."""
    combatant.privacy_acceptance.resolve(True)
    update_request = UpdateRequest(combatant=combatant)
    app.db.session.add(update_request)
    app.db.session.commit()

    data = dict(
        legal_name='Fred McFred',
        sca_name='Fred O''Fred',
        original_email='mcfred@mailinator.com',
        email='mcfred@mailinator.com',
        phone=2125551313,
        address1='125 Main Street',
        address2='',
        city='Othertown',
        province='ON',
        postal_code='A2A 2A2',
        token=update_request.token
    )

    client = app.test_client()
    response = client.put(
        '/api/combatant_update',
        data=json.dumps(data),
        content_type = 'application/json'
    )

    assert response.status_code == 200

    c = Combatant.query.filter(Combatant.email == data.get('email')).one()
    assert c.email == data.get('email')
    assert c.sca_name == data.get('sca_name')
    assert c.decrypted.get('legal_name') == data.get('legal_name')
    assert c.decrypted.get('phone') == data.get('phone')
    assert c.decrypted.get('address1') == data.get('address1')
    assert c.decrypted.get('address2') == data.get('address2')
    assert c.decrypted.get('city') == data.get('city')
    assert c.decrypted.get('province') == data.get('province')
    assert c.decrypted.get('postal_code') == data.get('postal_code')


def test_partial_update(app, combatant):
    """Test update on some fields."""
    combatant.privacy_acceptance.resolve(True)
    update_request = UpdateRequest(combatant=combatant)
    app.db.session.add(update_request)
    app.db.session.commit()

    data = dict(
        sca_name='Fred O''Fred',
        original_email='mcfred@mailinator.com',
        email='mcfred@mailinator.com',
        address2=None,
        postal_code='A2A 1A2',
        token=update_request.token
    )

    client = app.test_client()
    response = client.put(
        '/api/combatant_update',
        data=json.dumps(data),
        content_type = 'application/json'
    )

    assert response.status_code == 200

    c = Combatant.query.filter(Combatant.email == data.get('email')).one()

    # Things we changed
    assert c.sca_name == data.get('sca_name')
    assert c.decrypted.get('address2') == data.get('address2')
    assert c.decrypted.get('postal_code') == data.get('postal_code')

    # Things not changed
    assert c.email == data.get('email')
    assert c.decrypted.get('legal_name') == combatant.decrypted.get('legal_name')
    assert c.decrypted.get('phone') == combatant.decrypted.get('phone')
    assert c.decrypted.get('address1') == combatant.decrypted.get('address1')
    assert c.decrypted.get('city') == combatant.decrypted.get('city')
    assert c.decrypted.get('province') == combatant.decrypted.get('province')


def test_update_ignore(app, combatant):
    """Test update on fields that should be ignored.

    Combatant should not be able to self-serve update:
     - waiver date
     - date of birth (dob)

    (As cards and auths are done via separate API, we won't be that pedantic here.)

    """
    combatant.privacy_acceptance.resolve(True)
    update_request = UpdateRequest(combatant=combatant)
    app.db.session.add(update_request)
    app.db.session.commit()

    a_date = '2015-06-06'
    a_date_object = string_to_date(a_date)

    data = dict(
        original_email='mcfred@mailinator.com',
        email='mcfred@mailinator.com',
        token=update_request.token,
        dob=a_date,
        waiver_date=a_date
    )

    client = app.test_client()
    response = client.put(
        '/api/combatant_update',
        data=json.dumps(data),
        content_type = 'application/json'
    )

    assert response.status_code == 200

    c = Combatant.query.filter(Combatant.email == data.get('email')).one()

    # Things that should not change
    assert c.waiver.waiver_date != a_date_object
    assert c.decrypted.get('dob') is None
