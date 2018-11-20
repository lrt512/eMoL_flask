# -*- coding: utf-8 -*-
"""Handlers for user administration views."""

# standard library imports

# third-party imports
from flask import Blueprint, render_template, current_app

# application imports
from emol.decorators import admin_required
from emol.models import Discipline, Role, User

BLUEPRINT = Blueprint('user_admin', __name__)


@BLUEPRINT.route('/user-list', methods=['GET'])
@admin_required
def user_list():
    """Handle requests to view the user list.

    DataTables will use the user API to get user data via AJAX

    """
    return render_template('user/user_list.html')


@BLUEPRINT.route('/user-detail/<user_id>', methods=['GET'])
@admin_required
def user_detail(user_id):
    """Return the user detail form.

    Fill it in if a user ID is supplied

    Args:
        user_id: Optional id to fetch user data

    """
    if user_id == 'new':
        user = None
    else:
        user = User.query.filter(User.id == user_id).one()
        current_app.logger.debug('editing user %s', user)

    return render_template(
        'user/user_detail.html',
        user=user,
        roles=Role.query.all(),
        disciplines=Discipline.query.all()
    )
