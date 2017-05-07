import os
import pytest

import flask_login

# the app won't initialize without an environment variable pointing
# to the config file
os.environ['EMOL_CONFIG'] = '/home/vagrant/source/config/test/config.py'

SETUP_JSON = """{"encryption_key":"0123456789012345","global_waiver_date":true,"global_card_date":false,
"admin_emails":["ealdormere.emol@gmail.com"],
"disciplines":[{"name":"Rapier","slug":"rapier","authorizations":{"heavy-rapier":"Heavy Rapier",
"cut-thrust":"Cut & Thrust","two-weapon":"Two Weapon","parry-device":"Parry Device"},"marshals":{"marshal":"Marshal"}},
{"name":"Armoured Combat","slug":"armoured-combat","authorizations":{"weapon-shield":"Weapon & Shield",
"great-weapon":"Great Weapon","two-weapon":"Two Weapon","siege":"Siege"},"marshals":{"marshal":"Marshal"}}]}"""

from emol.app import create_app
the_app = create_app()
from emol.api.admin_api import SetupApi
SetupApi.test_setup(SETUP_JSON)

from emol.models import Combatant

@pytest.fixture(scope='session')
def app():
    """Flask-thing requires an 'app' fixture on everything."""
    yield the_app


# User fixtures


@pytest.fixture(scope='module')
def admin_user(app):
    """Log in the admin user"""
    from emol.models import User
    user = User.query.filter(User.email == 'ealdormere.emol@gmail.com').one()
    flask_login.login_user(user)

    yield user


@pytest.fixture(scope='session')
def unprivileged_user(app):
    from emol.models import User
    user = User(email='u_user@ealdormere.ca', system_admin=False)
    flask_login.login_user(user)

    yield user


@pytest.fixture(scope='function', params=['roles'])
def privileged_user(app, admin_user, unprivileged_user, request):
    """Log in a user and assign the given roles.

    Roles are given as a dict of lists:
    {
        None: [list of global roles],
        'discipline_slug': [list of roles for discipline_slug],
        ...
    }

    """
    # Log in admin user to assign roles
    flask_login.login_user(admin_user)

    for key, roles in request.param.items():
        unprivileged_user.add_roles(key, roles)

    # Log in now-privileged user for the test
    flask_login.logout_user()
    flask_login.login_user(unprivileged_user)

    yield unprivileged_user

    flask_login.logout_user()

    # Make sure unprivileged user really is
    unprivileged_user.roles.clear()
    assert len(unprivileged_user.roles) == 0


@pytest.fixture
def combatant_data():
    COMBATANT_DATA = dict(
        legal_name='Fred McFred',
        sca_name='Fred Fredsson',
        original_email='mcfred@mailinator.com',
        email='mcfred@mailinator.com',
        phone=2125551212,
        address1='123 Main Street',
        address2='Apartment 12',
        city='Anytown',
        province='ON',
        postal_code='A1A 1A1',
        waiver_date='2015-01-01'
    )

    yield COMBATANT_DATA

@pytest.fixture
@pytest.mark.parametrize(
    'privileged_user',
    [{ None: ['edit_combatant_info', 'edit_waiver_date'], 'rapier': ['edit_authorizations']}],
    indirect=True
)
def combatant(app, combatant_data):
    print(Combatant.query.all())
    c = Combatant.create(combatant_data)

    yield c

    app.db.session.delete(c)
    app.db.session.flush()
