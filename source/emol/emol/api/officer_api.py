# -*- coding: utf-8 -*-
"""Officer API endpoints.

This module implements REST API endpoints for managing officers.
Currently included are:

OfficerApi: Invoked to create or update officer records

OfficerListDataTable:   Invoked to retrieve a list of officer data formatted
                        for DataTables to consume

"""

# standard library imports

# third-party imports
from flask import request, jsonify, current_app
from flask_restful import Resource

# application imports
from emol.decorators import role_required
from emol.models import Officer


@current_app.api.route('/api/officer')
class OfficerApi(Resource):
    """Endpoint for officer creation and updates.

    Permitted methods: POST, PUT

    """

    @classmethod
    @role_required('can_edit_officer')
    def post(cls):
        """Create a new officer.

        Delegates incoming combatant data to the Officer model class

        See Officer.create_or_update for the JSON object specification

        Returns:
            200 if all is well
            400 if any error occurred

        """
        try:
            Officer.create_or_update(request.form)
        except Exception as exc:
            current_app.logger.exception('Error creating new officer')
            return {'message': str(exc)}, 400

    @classmethod
    @role_required('can_edit_officer')
    def put(cls):
        """Update an existing officer.

        Delegates incoming combatant data to the Officer model class. If
        valid data is passed and the officer does not exist, it will be
        created as if it were a POST request.

        See Officer.create_or_update for the JSON object specification

        Returns:
            200 if all is well
            400 if any error occurred

        """
        Officer.create_or_update(request.form)


@current_app.api.route('/api/officer-list-datatable')
class OfficerListDataTable(Resource):
    """Endpoint for the officer list DataTable.

    Permitted methods: GET

    """

    @classmethod
    @role_required('can_edit_officer')
    def get(cls):
        """Retrieve officer data for DataTables.

        Create a list of officer data including:
            Title
            Email
            Name
            Officer ID

        Returns:
            The list, JSON encoded

        """
        officers = {'data': [
            dict(
                title=o.title,
                email=o.email,
                name=o.sca_name,
                key=o.id
            ) for o in Officer.query.all()
        ]}
        return jsonify(officers)
