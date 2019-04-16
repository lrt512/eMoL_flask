"""Unit tests for Officer API."""

import json
import pytest


@pytest.fixture
def officer_data():
    return dict(
        title='Earl Marshal',
        short_title='KEM',
        legal_name='Fred McFred',
        sca_name='Fred Fredsson',
        email='mcfred@mailinator.com',
        phone=2125551212,
        address1='123 Main Street',
        address2='Apartment 12',
        city='Anytown',
        province='ON',
        postal_code='A1A 1A1',
        note = None,
        discipline = 'armoured-combat'
    )


def test_create_anonymous(app, officer_data):
    """Test create officer as anonymous."""
    client = app.test_client()
    response = client.post('/api/officer', data=officer_data)
    assert response.status_code == 401


def test_create_admin(app, admin_user, login_client, officer_data):
    """Test create and delete user vi API as admin."""
    response = login_client.post(
        '/api/officer',
        data=officer_data
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'privileged_user',
    [{None: ['edit_combatant_info']}],
    indirect=True
)
def test_create_unprivileged(privileged_user, login_client, officer_data):
    """Test create user as with a valid but unprivileged user."""
    response = login_client.post(
        '/api/officer',
        data=officer_data,
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'privileged_user',
    [{None: ['edit_officer_info']}],
    indirect=True
)
def test_create_authorized(app, privileged_user, login_client, officer_data, ):
    """Test create user as with a valid and privileged user."""
    response = login_client.post(
        '/api/officer',
        data=officer_data
    )
    assert response.status_code == 200

