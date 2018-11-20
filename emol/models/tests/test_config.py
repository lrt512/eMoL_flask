"""Unit tests for Config model."""
import pytest
from datetime import date, datetime

from emol.models import Config


def test_config_int(app):
    """Test get/set int."""
    Config.set('thing', 5)
    value = Config.get('thing')
    assert isinstance(value, int)
    assert value == 5


def test_config_str(app):
    """Test get/set str."""
    Config.set('thing', 'foo')
    value = Config.get('thing')
    assert isinstance(value, str)
    assert value == 'foo'


def test_config_bool_true(app):
    """Test get/set boolean True."""
    Config.set('thing', True)
    value = Config.get('thing')
    assert isinstance(value, bool)
    assert value is True


def test_config_bool_false(app):
    """Test get/set boolean False."""
    Config.set('thing', False)
    value = Config.get('thing')
    assert isinstance(value, bool)
    assert value is False


def test_config_float(app):
    """Test get/set float."""
    Config.set('thing', 1.001)
    value = Config.get('thing')
    assert isinstance(value, float)
    assert value == 1.001


def test_config_date(app):
    """Test get/set date."""
    d = date.today()
    Config.set('thing', d)
    value = Config.get('thing')
    assert isinstance(value, date)
    assert value == d


def test_config_datetime(app):
    """Test get/set datetime."""
    d = datetime.now()
    Config.set('thing', d)
    value = Config.get('thing')
    assert isinstance(value, datetime)
    assert value == d


def test_config_list(app):
    """Test get/set list."""
    l = [1, 'foo', True]
    Config.set('thing', l)
    value = Config.get('thing')
    assert isinstance(value, list)
    for v in l:
        assert v in value


def test_waiver_reminders(app):
    """Test for the waiver reminder times."""
    reminders = Config.get('waiver_reminders')
    assert len(reminders) == 2
    assert 30 in reminders
    assert 60 in reminders