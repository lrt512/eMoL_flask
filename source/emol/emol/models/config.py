# -*- coding: utf-8 -*-
"""Global configuration model.

General storage as key-value pairs for config items

"""

# standard library imports
from datetime import datetime, date
from dateutil import parser
import json

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

    data_types = [str, int, float, datetime, date, bool, list]

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
        elif isinstance(value, list):
            config.value = json.dumps(value)
            config.type = 6
        elif isinstance(value, bool):
            config.value = '1' if value else '0'
            config.type = 5
        elif type(value) is date:
            # Need to use the more explict check here as isinstance will
            # lead you astray if value is a datetime
            config.value = value.isoformat()
            config.type = 4
        elif type(value) is datetime:
            config.value = value.isoformat()
            config.type = 3
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
            return parser.parse(config.value)
        elif config.type == 4:
            return parser.parse(config.value).date()
        elif config.type == 5:
            return True if config.value == '1' else False
        elif config.type == 6:
            return json.loads(config.value)
        else:
            return cls.data_types[config.type](config.value)
