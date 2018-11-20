import pytest

from werkzeug.exceptions import Unauthorized

from emol.models import Combatant, Card, CardReminder


@pytest.mark.parametrize(
    'privileged_user',
    [{ 'rapier': ['edit_authorizations']}],
    indirect=True
)
def test_authorizations_authorized(app, combatant, privileged_user):
    """Test adding authorizations."""
    card = combatant.get_card('rapier')
    card.add_authorization('heavy-rapier')
    card.add_authorization('two-weapon')

    assert len(card.reminders) == 3
    assert CardReminder.query.count() == 3

    card.remove_authorization('two-weapon')
    assert len(card.authorizations) == 1


@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info']}],
    indirect=True
)
def test_authorizations_unauthorized(app, combatant, privileged_user):
    """Test adding authorizations."""
    #with pytest.raises(Exception):
    #    card = combatant.get_card('rapier')
    pass

@pytest.mark.parametrize(
    'privileged_user',
    [],
    indirect=True
)
def test_marshal_unauthorized(app, combatant, privileged_user):
    """Test adding authorizations."""
    card = combatant.get_card('rapier')

    with pytest.raises(Exception):
        card.add_warrant('marshal')


@pytest.mark.parametrize(
    'privileged_user',
    [{ 'rapier': ['edit_authorizations', 'edit_marshal']}],
    indirect=True
)
def test_marshal_authorized(app, combatant, privileged_user):
    """Test adding authorizations."""
    card = combatant.get_card('rapier')

    card.add_warrant('marshal')
    assert len(card.warrants) == 1

