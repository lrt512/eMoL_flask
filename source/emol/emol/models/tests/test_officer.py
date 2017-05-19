"""Test officer model."""

import copy
import pytest

from emol.models import Officer, Discipline


@pytest.fixture
def rapier(app):
    discipline = Discipline.find('rapier')

    yield discipline


@pytest.fixture
def armoured(app):
    discipline = Discipline.find('armoured-combat')

    yield discipline



@pytest.fixture
def kem_info(armoured):
    return dict(
        title='Kingdom Earl Marshal',
        short_title='KEM',
        legal_name='Fred McFred',
        sca_name='Frederick Fredsson',
        email='mcfred@ealdormere.ca',
        address1='123 Main St.',
        city='Anytown',
        state='ON',
        postal_code='H0H0H0',
        phone=2125551212,
        note='The KEM',
        discipline_id=armoured.id
    )


@pytest.fixture
def kem(app, kem_info):
    """Create the KEM officer."""
    officer = Officer.create_or_update(kem_info)

    yield(officer)

    app.db.session.delete(officer)
    app.db.session.commit()


@pytest.fixture
def krm_info(rapier):
    return dict(
        title='Kingdom Rapier Marshal',
        short_title='KRM',
        legal_name='Fred McFred',
        sca_name='Frederick Fredsson',
        email='mcfred@ealdormere.ca',
        address1='123 Main St.',
        city='Anytown',
        state='ON',
        postal_code='H0H0H0',
        phone=2125551212,
        note='The KRM',
        discipline_id=rapier.id
    )


def test_create_kem(app, kem, armoured):
    """Test create officer (KEM)."""

    assert kem is not None
    assert kem.parent is None
    assert kem.discipline is armoured


def test_create_krm(app, kem, rapier, krm_info):
    """Test create officer (KRM)."""
    krm_info['parent_id'] = kem.id
    krm = Officer.create_or_update(krm_info)

    assert krm is not None
    assert krm.parent is kem
    assert krm.discipline is rapier

    app.db.session.delete(krm)
    app.db.session.commit()


def test_missing_data(app, kem_info):
    """Validate required data enforcement."""
    # Exclude the keys that are allowed to be empty
    keys = [k for k in kem_info.keys()
            if k not in Officer.allowed_empty]

    for key in keys:
        data = copy.copy(kem_info)
        del data[key]

        with pytest.raises(Exception):
            Officer.create_or_update(data)

