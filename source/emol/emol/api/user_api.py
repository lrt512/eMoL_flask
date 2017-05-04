# -*- coding: utf-8 -*-
"""User API endpoints.

This module implements REST API endpoints for managing users.
Currently included are:

UserApi: Invoked to create or update user records

UserListDataTable:  Invoked to retrieve a list of user data formatted for
                    DataTables to consume

"""

# standard library imports

# third-party imports
from flask import request, jsonify, current_app, abort
from flask_restful import Resource

# application imports
from emol.decorators import admin_required
from emol.models import Discipline, User


@current_app.api.route('/api/user')
class UserApi(Resource):
    """Endpoint for user creation and updates.

    Permitted methods: POST, PUT

    """

    @classmethod
    @admin_required
    def post(cls):
        """Create a new user.

        Delegates incoming combatant data to the user model class

        See user.create_or_update for the JSON object specification

        Returns:
            200 if all is well
            400 if any error occurred

        """
        # TODO: This should use the .json property
        email = request.form['email']
        user = User.query.filter(User.email == email).one_or_none()
        if user is None:
            user = User(email=email)

        # Update roles
        cls.update_roles(user)

    @classmethod
    @admin_required
    def put(cls):
        """Update an existing user.

        Delegates incoming combatant data to the user model class. If
        valid data is passed and the user does not exist, it will be
        created as if it were a POST request.

        See user.create_or_update for the JSON object specification

        Returns:
            200 if all is well
            400 if any error occurred

        """
        # TODO: This should use the .json property
        try:
            user = User.query.filter(User.id == request.form['id']).one()
            user.email = request.form['email']

            # Update roles
            cls.update_roles(user)
        except Exception as exc:
            print(exc)
            abort(400)

    @classmethod
    def update_roles(cls, user):
        """Update a user's roles.

        Given a user, invoke roles_for for the global case and then for all
        disciplines.

        """
        # Global roles
        UserApi.roles_for(user, None)

        # Roles for disciplines
        for discipline in Discipline.query.all():
            UserApi.roles_for(user, discipline.slug)

    @classmethod
    def roles_for(cls, user, discipline):
        """Manage roles for the user.

        Based on the roles listed in the request data, add or remove roles
        for this user.

        Args:
            user: The user in question
            discipline: The discipline to apply

        Returns:

        """
        delete = []
        add = []

        # Roles as selected in the UI
        assigned_roles = request.form.getlist(
            'global' if discipline is None else discipline)

        # Roles the user already has
        current_roles = user.roles_for(discipline)

        # Roles to be removed
        for current_role in current_roles:
            if current_role not in assigned_roles:
                delete.append(current_role)

        # Roles to be added
        for assigned_role in assigned_roles:
            if assigned_role not in current_roles:
                add.append(assigned_role)

        # Update
        for role in delete:
            user.remove_role(discipline, role)

        for role in add:
            user.add_role(discipline, role)


@current_app.api.route('/api/user-list-datatable')
class UserListDataTable(Resource):
    """Endpoint for the user list DataTable.

    Permitted methods: GET

    """

    @classmethod
    @admin_required
    def get(cls):
        """Retrieve user data for DataTables.

        Create a list of user data including:
            Email
            user ID

        Returns:
            The list, JSON encoded

        """
        users = {'data': [
            dict(
                email=u.email,
                disciplines='None',
                key=u.id
            ) for u in User.query.all() if u.system_admin is False
        ]}

        return jsonify(users)
