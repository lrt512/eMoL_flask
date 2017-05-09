import pytest

from werkzeug.exceptions import Unauthorized

from emol.exception.privacy_acceptance import PrivacyPolicyNotAccepted
from emol.models import Combatant, Card, PrivacyAcceptance
from emol.utility.testing import Mockmail


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info']}],
    indirect=True
)
def test_privacy_not_accepted(app, combatant, privileged_user):
    """Test combatant that has not accepted yet."""
    assert combatant.card_id is None
    assert combatant.accepted_privacy_policy is False
    with pytest.raises(PrivacyPolicyNotAccepted):
        url = combatant.card_url


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info']}],
    indirect=True
)
def test_privacy_declined(app, combatant, privileged_user):
    """Test declined privacy policy."""
    resolution = combatant.privacy_acceptance.resolve(False)
    assert resolution.get('accepted') is False

    # We still have a reference to the combatant, but it should be
    # purged from the database now
    assert Combatant.query.filter(
        Combatant.id == combatant.id).one_or_none() is None


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info']}],
    indirect=True
)
def test_privacy_accepted(app, combatant, privileged_user):
    """Test accepted privacy policy."""
    with Mockmail('emol.models.privacy_acceptance', True):
        resolution = combatant.privacy_acceptance.resolve(True)

    assert combatant.card_url is not None
    assert resolution.get('card_url') == combatant.card_url
    assert resolution.get('accepted') is True
