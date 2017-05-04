# -*- coding: utf-8 -*-
"""Initialize cron."""

# standard library imports
import types

# third-party imports
from flask import current_app
from flask_restful import Api

# application imports


def init_api():
    """Set up the API."""
    current_app.logger.info('Initialize API')
    current_app.api = Api(current_app)

    # Create a decorator for flask-restful routes
    # From http://flask.pocoo.org/snippets/129/
    def api_route(self, *args, **kwargs):
        """Wrap the add_resource call in a wrapper."""
        def wrapper(cls):
            """Add the API resource."""
            self.add_resource(cls, *args, **kwargs)
            return cls

        return wrapper

    current_app.api.route = types.MethodType(api_route, current_app.api)

    # pylint will complain about this but it needs to be
    # here to actually initialize the API
    # pylint: disable=unused-import
    # pylint: disable=unused-variable
    import emol.api
