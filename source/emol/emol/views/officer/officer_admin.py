# -*- coding: utf-8 -*-
"""Handlers for officer administration views."""

# standard library imports

# third-party imports
from flask import Blueprint, render_template, current_app

# application imports
from emol.decorators import admin_required
from emol.models import Discipline, Officer

BLUEPRINT = Blueprint('officer_admin', __name__)


@BLUEPRINT.route('/officer-list', methods=['GET'])
@admin_required
def officer_list():
    """Handle requests to view the officer list.

    DataTables will use the officer API to get officer data via AJAX

    """
    return render_template(
        'officer/officer_list.html'
    )


@BLUEPRINT.route('/officer-detail/<officer_id>', methods=['GET'])
@admin_required
def get(officer_id):
    """Return the officer detail form.

    Fill it in if an officer ID is supplied

    Args:
        officer_id: Optional id to fetch officer data

    """
    if officer_id == 'new':
        officer = None
    else:
        officer = Officer.query.filter(Officer.id == officer_id).one()
        current_app.logger.debug('editing officer %s', officer)

    if officer:
        print(
            officer.parent.short_title if
            officer and officer.parent else
            None
        )

    return render_template(
        'officer/officer_detail.html',
        officer=officer,
        disciplines=[d for d in Discipline.query.all()
                     if officer is None or d not in officer.children],
        discipline_slug=(officer.discipline.slug
                         if officer and officer.discipline else None),
        parent_slug=(officer.parent.short_title
                     if officer and officer.parent else None),
        officers=[o for o in Officer.query.all()
                  if officer != o and o not in officer.children]
    )
