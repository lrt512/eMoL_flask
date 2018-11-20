"""Unit tests for Combatant API."""

import json
import pytest


def test_create_anonymous(app, combatant_data):
    """Test create user as anonymous."""
    client = app.test_client()
    response = client.post('/api/combatant', data=combatant_data)
    assert response.status_code == 401


def test_create_admin(app, admin_user, login_client, combatant_data):
    """Test create and delete user vi API as admin."""
    response = login_client.post(
        '/api/combatant',
        data=json.dumps(combatant_data),
        content_type = 'application/json'
    )

    assert response.status_code == 200
    uuid = response.json.get('uuid')
    assert uuid is not None

    response = login_client.delete('/api/combatant/{0}'.format(uuid))
    assert response.status_code == 200


def test_create_unprivileged(unprivileged_user, login_client, combatant_data):
    """Test create user as with a valid but unprivileged user."""
    response = login_client.post(
        '/api/combatant',
        data=json.dumps(combatant_data),
        content_type = 'application/json'
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'privileged_user',
    [{None: ['edit_combatant_info']}],
    indirect=True
)
def test_create_authorized(app, privileged_user, login_client, combatant_data, ):
    """Test create user as with a valid and privileged user."""
    response = login_client.post(
        '/api/combatant',
        data=json.dumps(combatant_data),
        content_type = 'application/json'
    )
    assert response.status_code == 200
    uuid = response.json.get('uuid')
    assert uuid is not None

    response = login_client.delete('/api/combatant/{0}'.format(uuid))
    assert response.status_code == 200

