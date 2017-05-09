"""Unit tests for card and waiver reminders."""
import pytest

from emol.utility.testing import Mockmail


@pytest.mark.parametrize(
    'privileged_user',
    [{ 'rapier':['edit_authorizations']}],
    indirect=True
)
def test_create_reminders(app, combatant, privileged_user):
    """Test card and waiver reminder creation."""
    card = combatant.get_card('rapier', create=True)
    assert len(card.reminders) == 3
    assert len(combatant.waiver.reminders) == 3


@pytest.mark.parametrize(
    'privileged_user',
    [{ 'rapier':['edit_authorizations']}],
    indirect=True
)
def test_card_mail(app, combatant, privileged_user):
    """Test sending emails for card reminder/expiry."""
    card = combatant.get_card('rapier', create=True)
    for reminder in card.reminders:
        with Mockmail('emol.models.card', True):
            reminder.mail()


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_waiver_date']}],
    indirect=True
)
def test_waiver_mail(app, combatant, privileged_user):
    """Test sending emails for waiver reminder/expiry."""
    for reminder in combatant.waiver.reminders:
        with Mockmail('emol.models.waiver', True):
            reminder.mail()
