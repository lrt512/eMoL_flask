import pytest

from werkzeug.exceptions import Unauthorized

from emol.models import Combatant, Card, CardReminder
from emol.utility.testing import Mockmail

@pytest.fixture(scope='module')
def client(app):
    client = app.test_client()

    yield client


def test_card_request_no_combatant(app, client):
    """Test requesting card for non-existent combatant."""
    with Mockmail('emol.views.home', False):
        response = client.post(
            '/request-card',
            data={'request-card-email': 'foo@ealdormere.ca'}
        )
        assert 'No combatant found' in response.data.decode()


def test_card_request_no_privacy(app, combatant, client):
    """Test requesting card for combatant without privacy acceptance."""
    with Mockmail('emol.views.home', False):
        response = client.post(
            '/request-card',
            data={'request-card-email': combatant.email}
        )
        print(response.data)
        assert 'not yet accepted' in response.data.decode()


def test_card_request_privacy_accepted(app, combatant, client):
    """Test requesting card for combatant with privacy acceptance."""
    with Mockmail('emol.models.privacy_acceptance', None):
        combatant.privacy_acceptance.resolve(True)

    with Mockmail('emol.views.home', True):
        response = client.post(
            '/request-card',
            data={'request-card-email': combatant.email}
        )
        assert 'An email has been sent' in response.data.decode()


def test_card_request_privacy_declined(app, combatant, client):
    """Test requesting card for combatant with privacy declined."""
    with Mockmail('emol.models.privacy_acceptance', None):
        combatant.privacy_acceptance.resolve(False)

    with Mockmail('emol.views.home', False):
        response = client.post(
            '/request-card',
            data={'request-card-email': combatant.email}
        )
        assert 'No combatant found' in response.data.decode()


def test_info_update_no_combatant(app, client):
    """Test info update for non-existent combatant."""
    with Mockmail('emol.views.home', False):
        response = client.post(
            '/update-info',
            data={'update-info-email': 'foo@ealdormere.ca'}
        )
        assert 'No combatant found' in response.data.decode()


def test_info_update_no_privacy(app, combatant, client):
    """Test info update for combatant without privacy acceptance."""
    with Mockmail('emol.views.home', False):
        response = client.post(
            '/update-info',
            data={'update-info-email': combatant.email}
        )
        print(response.data)
        assert 'not yet accepted' in response.data.decode()


def test_info_update_privacy_accepted(app, combatant, client):
    """Test info update for combatant with privacy acceptance."""
    with Mockmail('emol.models.privacy_acceptance', None):
        combatant.privacy_acceptance.resolve(True)

    with Mockmail('emol.views.home', True):
        response = client.post(
            '/update-info',
            data={'update-info-email': combatant.email}
        )
        assert 'An email has been sent' in response.data.decode()


def test_info_update_privacy_declined(app, combatant, client):
    """Test info update for combatant with privacy declined."""
    with Mockmail('emol.models.privacy_acceptance', None):
        combatant.privacy_acceptance.resolve(False)

    with Mockmail('emol.views.home', False):
        response = client.post(
            '/update-info',
            data={'update-info-email': combatant.email}
        )
        assert 'No combatant found' in response.data.decode()

