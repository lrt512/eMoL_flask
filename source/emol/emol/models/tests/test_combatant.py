import pytest

from werkzeug.exceptions import Unauthorized

from emol.models import Combatant, Card, CardReminder


def test_create_anonymous(app, combatant_data):
    """Test create user as anonymous."""

    with pytest.raises(Unauthorized):
        combatant = Combatant.create(combatant_data)


def test_create_admin(app, admin_user, combatant_data):
    """Test create user as admin."""
    combatant = Combatant.create(combatant_data)
    assert combatant is not None

    app.db.session.delete(combatant)


def test_create_unprivileged(app, unprivileged_user, combatant_data):
    """Test create user as with a valid but unprivileged user."""
    with pytest.raises(Unauthorized):
        combatant = Combatant.create(combatant_data)


@pytest.mark.parametrize(
    'privileged_user',
    [{None: ['edit_combatant_info']}],
    indirect=True
)
def test_create_authorized(app, privileged_user, combatant_data):
    """Test create user as with a valid and privileged user."""
    combatant = Combatant.create(combatant_data)
    assert combatant is not None

    app.db.session.delete(combatant)


