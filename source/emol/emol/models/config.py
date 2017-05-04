# -*- coding: utf-8 -*-
"""Global configuration model.

General storage as key-value pairs for config items

"""

# standard library imports
from datetime import datetime, date
import dateutil.parser

# third-party imports
from flask import current_app as app

# application imports


class Config(app.db.Model):
    """Key-Value config storage.

    This table is used to store configuration items as needed.
    It currently supports:
        - string
        - integer
        - float
        - datetime
        - date

    """

    key = app.db.Column(app.db.String(255), primary_key=True)
    value = app.db.Column(app.db.String(32767), nullable=True)
    type = app.db.Column(app.db.Integer, nullable=True)

    data_types = [str, int, float, datetime, date, bool]

    @classmethod
    def set(cls, key, value):
        """Set a value."""
        config = cls.query.filter(Config.key == key).one_or_none()
        if config is None:
            config = Config(key=key, value=None, type=None)
            app.db.session.add(config)

        if value is None:
            config.value = None
            config.type = None
        elif isinstance(value, bool):
            config.value = '1' if value else '0'
            config.type = 5
        elif isinstance(value, datetime):
            config.value = value.isoformat()
            config.type = 3
        elif isinstance(value, date):
            config.value = value.isoformat()
            config.type = 4
        else:
            config.value=str(value)
            config.type=cls.data_types.index(type(value))

        app.db.session.commit()

    @classmethod
    def get(cls, key, default=None):
        """Get a value with optional default."""
        config = Config.query.filter(Config.key == key).one_or_none()
        if config is None:
            return default

        if config.value is None:
            return None

        if config.type == 3:
            return dateutil.parser.parse(config.value)
        elif config.type == 4:
            return dateutil.parser.parse(config.value)
        elif config.type == 5:
            return True if config.value == '1' else False
        else:
            return cls.data_types[config.type](config.value)
