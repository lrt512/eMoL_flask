"""Unit tests for card and waiver reminders."""
import pytest

@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date'], 'rapier':['edit_authorizations']}],
    indirect=True
)
def test_create_reminders(app, privileged_user, combatant):
    """Test card and waiver reminder creation."""
    card = combatant.get_card('rapier', create=True)
    assert len(card.reminders) == 3
    assert len(combatant.waiver.reminders) == 3


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date'], 'rapier':['edit_authorizations']}],
    indirect=True
)
def test_reminder_mail(app, privileged_user, combatant):
    """Test sending emails for card reminder/expiry.

    Check mailcatcher to make sure they went

    """
    card = combatant.get_card('rapier', create=True)
    for reminder in card.reminders:
        reminder.mail()


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date']}],
    indirect=True
)
def test_waiver_mail(app, privileged_user, combatant):
    """Test sending emails for waiver reminder/expiry.

    Check mailcatcher to make sure they went

    """
    for reminder in combatant.waiver.reminders:
        reminder.mail()