"""Unit tests for import API."""

from io import BytesIO
import pytest

from emol.models import Combatant


@pytest.fixture
def rapier_csv():
    file = BytesIO(bytes("""legal_name, sca_name, email, phone, address1, address2, city, province, postal_code, waiver_date, dob, member_number, member_expiry, twoweapon, cutthrust, heavyrapier, parrydevice, marshal, card_date
Random Dude, Fred McFred, fred@mailinator.com, 2125551212, 123 Main Street, , Anytown, ON, H0H 0H0, 2015-01-01, , , , no, no, yes, no, no, 2018-06-30""",
    'UTF-8'))

    return file


def test_import(app, admin_user, login_client, rapier_csv):
    """Test basic import."""
    response = login_client.post(
        '/api/import',
        data={
            'discipline': 'rapier',
            'file': (rapier_csv, 'rapier.csv')
        }
    )

    assert response.status_code == 200
    assert Combatant.query.count() == 1
