import pytest

from werkzeug.exceptions import Unauthorized

from emol.models import Combatant, Card, CardReminder
from emol.utility.testing import Mockmail


def test_create_anonymous(app, combatant_data):
    """Test create user as anonymous."""

    with pytest.raises(Unauthorized):
        combatant = Combatant.create(combatant_data)


def test_create_admin(app, combatant_data, admin_user):
    """Test create user as admin."""
    with Mockmail('emol.models.privacy_acceptance', True):
        combatant = Combatant.create(combatant_data)

    assert combatant is not None

    app.db.session.delete(combatant)
    app.db.session.commit()


def test_create_unprivileged(app, combatant_data, unprivileged_user):
    """Test create user as with a valid but unprivileged user."""
    with pytest.raises(Unauthorized):
        combatant = Combatant.create(combatant_data)


@pytest.mark.parametrize(
    'privileged_user',
    [{None: ['edit_combatant_info']}],
    indirect=True
)
def test_create_authorized(app, combatant_data, privileged_user):
    """Test create user as with a valid and privileged user."""
    with Mockmail('emol.models.privacy_acceptance', True):
        combatant = Combatant.create(combatant_data)

    assert combatant is not None

    app.db.session.delete(combatant)
    app.db.session.commit()


