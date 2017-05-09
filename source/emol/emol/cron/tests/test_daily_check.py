"""Unit tests for card and waiver reminders."""
import pytest

from emol.cron.daily_check import daily_check
from emol.models import WaiverReminder
from emol.utility.testing import Mocktoday, Mockmail

# Card
@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date'], 'rapier':['edit_authorizations']}],
    indirect=True
)
def test_daily_check_card(app, privileged_user, combatant):
    """Test daily check consuming card reminders."""
    card = combatant.get_card('rapier', create=True)
    assert len(card.reminders) == 3

    card_dates = [r.reminder_date for r in card.reminders]

    # dates on the calendar happen in chronological order
    card_dates.sort()

    while len(card_dates) > 0:
        date = card_dates.pop(0)
        with Mocktoday('emol.cron.daily_check', date):
            with Mockmail('emol.models.card', True):
                daily_check()
                assert len(card.reminders) == len(card_dates)

    assert len(card.reminders) == 0

# Waiver

@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date']}],
    indirect=True
)
def test_daily_check_waiver(app, privileged_user, combatant):
    """Test daily check consuming waiver reminders."""
    assert len(combatant.waiver.reminders) == 3

    waiver_dates = [r.reminder_date for r in combatant.waiver.reminders]

    # dates on the calendar happen in chronological order
    waiver_dates.sort()

    while len(waiver_dates) > 0:
        date = waiver_dates.pop(0)
        with Mocktoday('emol.cron.daily_check', date):
            with Mockmail('emol.models.waiver', True):
                daily_check()
                assert len(combatant.waiver.reminders) == len(waiver_dates)

    assert len(combatant.waiver.reminders) == 0


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date']}],
    indirect=True
)
def test_daily_check_waiver_renew_first(app, privileged_user, combatant):
    """Test daily check with waiver renew after first reminder."""
    waiver_dates = [r.reminder_date for r in combatant.waiver.reminders]

    # dates on the calendar happen in chronological order
    waiver_dates.sort()

    # Send the first reminder
    with Mocktoday('emol.cron.daily_check', waiver_dates[0]):
        with Mockmail('emol.models.waiver', True):
            daily_check()
            assert len(combatant.waiver.reminders) == 2

    # Now the combatant renews
    combatant.waiver.renew()
    assert len(combatant.waiver.reminders) == 3
    assert WaiverReminder.query.filter(WaiverReminder.waiver_id == combatant.waiver.id).count() == 3

    # Now send all three new reminders
    waiver_dates = [r.reminder_date for r in combatant.waiver.reminders]

    # dates on the calendar happen in chronological order
    waiver_dates.sort()

    while len(waiver_dates) > 0:
        date = waiver_dates.pop(0)
        with Mocktoday('emol.cron.daily_check', date):
            with Mockmail('emol.models.waiver', True):
                daily_check()
                assert len(combatant.waiver.reminders) == len(waiver_dates)

    assert len(combatant.waiver.reminders) == 0


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date']}],
    indirect=True
)
def test_daily_check_waiver_renew_second(app, privileged_user, combatant):
    """Test daily check with waiver renew after second reminder."""
    waiver_dates = [r.reminder_date for r in combatant.waiver.reminders]

    # dates on the calendar happen in chronological order
    waiver_dates.sort()

    # Send the first reminder
    with Mocktoday('emol.cron.daily_check', waiver_dates[0]):
        with Mockmail('emol.models.waiver', True):
            daily_check()
            assert len(combatant.waiver.reminders) == 2

    # Send the second reminder
    with Mocktoday('emol.cron.daily_check', waiver_dates[1]):
        with Mockmail('emol.models.waiver', True):
            daily_check()
            assert len(combatant.waiver.reminders) == 1

    # Now the combatant renews
    combatant.waiver.renew()
    assert len(combatant.waiver.reminders) == 3
    assert WaiverReminder.query.filter(WaiverReminder.waiver_id == combatant.waiver.id).count() == 3

    # Now send all three new reminders
    waiver_dates = [r.reminder_date for r in combatant.waiver.reminders]

    # dates on the calendar happen in chronological order
    waiver_dates.sort()

    while len(waiver_dates) > 0:
        date = waiver_dates.pop(0)
        with Mocktoday('emol.cron.daily_check', date):
            with Mockmail('emol.models.waiver', True):
                daily_check()
                assert len(combatant.waiver.reminders) == len(waiver_dates)

    assert len(combatant.waiver.reminders) == 0


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date']}],
    indirect=True
)
def test_daily_check_waiver_renew_expired(app, privileged_user, combatant):
    """Test daily check with waiver renew after expiry."""
    waiver_dates = [r.reminder_date for r in combatant.waiver.reminders]

    # dates on the calendar happen in chronological order
    waiver_dates.sort()

    # Send the first reminder
    while len(waiver_dates) > 0:
        date = waiver_dates.pop(0)
        with Mocktoday('emol.cron.daily_check', date):
            with Mockmail('emol.models.waiver', True):
                daily_check()
                assert len(combatant.waiver.reminders) == len(waiver_dates)

    # Now the combatant renews
    combatant.waiver.renew()
    assert len(combatant.waiver.reminders) == 3
    assert WaiverReminder.query.filter(WaiverReminder.waiver_id == combatant.waiver.id).count() == 3

    # Now send all three new reminders
    waiver_dates = [r.reminder_date for r in combatant.waiver.reminders]

    # dates on the calendar happen in chronological order
    waiver_dates.sort()

    while len(waiver_dates) > 0:
        date = waiver_dates.pop(0)
        with Mocktoday('emol.cron.daily_check', date):
            with Mockmail('emol.models.waiver', True):
                daily_check()
                assert len(combatant.waiver.reminders) == len(waiver_dates)

    assert len(combatant.waiver.reminders) == 0

