# -*- coding: utf-8 -*-
"""Combatant API endpoints.

This module implements the REST API endpoints for managing combatants.
Currently included are:

CombatantApi: Invoked to create or update combatant records

CombatantListDataTable: Invoked to retrieve a list of combatant data formatted
                        for DataTables to consume

"""

# standard library imports

# third-party imports
from flask import request, jsonify, current_app
from flask_restful import Resource, fields

# application imports
from emol.decorators import login_required
from emol.models import Combatant


@current_app.api.route('/api/combatant/<string:uuid>')
class CombatantApi(Resource):
    """Endpoint for combatant creation and updates.

    Permitted methods: POST, PUT

    """

    @classmethod
    @login_required
    def post(cls):
        """Create a new combatant.

        Delegates incoming combatant data to the Combatant model class

        See Combatant.create_or_update for the JSON object specification

        Returns:
            200 if all is well
            400 if any error occurred

        """
        combatant = Combatant.create(request.json)
        return {'uuid': combatant.uuid}

    @classmethod
    @login_required
    def put(cls, uuid):
        """Update an existing combatant.

        Delegates incoming combatant data to the Combatant model class. If
        valid data is passed and the combatant does not exist, it will be
        created as if it were a POST request.

        See Combatant.create_or_update for the JSON object specification

        Returns:
            200 if all is well
            400 if any error occurred

        """
        combatant = Combatant.get_by_uuid(uuid)
        combatant.update(request.json)
        return {'uuid': combatant.uuid}

    @classmethod
    @login_required
    def delete(cls, uuid):
        """Delete a combatant.

        Returns:
            200 if all is well
            400 if any error occurred

        """
        combatant = Combatant.get_by_uuid(uuid)
        current_app.db.session.delete(combatant)
        current_app.db.session.commit()


@current_app.api.route('/api/combatant/<string:uuid>/authorization')
class CombatantAuthorizationApi(Resource):
    """Endpoint for managing combatant authorizations

    Permitted methods: POST, DELETE

    """

    @classmethod
    @login_required
    def post(cls, uuid):
        """Add an authorization

        Returns:
            200 if all is well
            400 if any error occurred

        """
        combatant = Combatant.get_by_uuid(uuid)

        discipline = request.json.get('discipline')
        card = combatant.get_card(discipline, create=True)
        if card is None:
            return

        slug = request.json.get('slug')
        card.add_authorization(slug)

    @classmethod
    @login_required
    def delete(cls, uuid):
        """Remove an authorization

        Returns:
            200 if all is well
            400 if any error occurred

        """
        combatant = Combatant.get_by_uuid(uuid)

        discipline = request.json.get('discipline')
        card = combatant.get_card(discipline)
        if card is None:
            return

        slug = request.json.get('slug')
        card.remove_authorization(slug)


@current_app.api.route('/api/combatant/<string:uuid>/warrant')
class CombatantWarrantApi(Resource):
    """Endpoint for managing combatant warrants

    Permitted methods: POST, DELETE

    """

    @classmethod
    @login_required
    def post(cls, uuid):
        """Add a warrant

        Returns:
            200 if all is well
            400 if any error occurred

        """
        combatant = Combatant.get_by_uuid(uuid)

        discipline = request.json.get('discipline')
        card = combatant.get_card(discipline, create=True)
        if card is None:
            return

        slug = request.json.get('slug')
        card.add_warrant(slug)

    @classmethod
    @login_required
    def delete(cls, uuid):
        """Remove an authorization

        Returns:
            200 if all is well
            400 if any error occurred

        """
        combatant = Combatant.get_by_uuid(uuid)

        discipline = request.json.get('discipline')
        card = combatant.get_card(discipline)
        if card is None:
            return

        slug = request.json.get('slug')
        card.remove_warrant(slug)


@current_app.api.route('/api/combatant-list-datatable')
class CombatantListDataTable(Resource):
    """Endpoint for the combatant DataTable.

    Permitted methods: GET

    """

    @classmethod
    @login_required
    def get(cls):
        """Retrieve combatant data for DataTables.

        Create a list of combatant data including:
            Legal Name
            SCA Name
            Card ID
            Privacy policy accepted (boolean)
            Combatant UUID

        Returns:
            The list, JSON encoded

        """
        combatants = {'data': [
            dict(
                legal_name=c.decrypted.get('legal_name'),
                sca_name=c.sca_name,
                card_id=c.card_id,
                accepted_privacy_policy=c.accepted_privacy_policy,
                uuid=c.uuid
            ) for c in Combatant.query.all()
        ]}
        return jsonify(combatants)
