# -*- coding: utf-8 -*-
"""Handlers for combatant administration views."""

# standard library imports
import logging
from datetime import date

# third-party imports
from flask import Blueprint, render_template, current_app
from flask_login import current_user

# application imports
from emol.decorators import login_required
from emol.exception.combatant import CombatantDoesNotExist
from emol.models import Combatant, Discipline, Role, CombatantAuthorization, Warrant
from emol.utility.date import add_years

BLUEPRINT = Blueprint('combatant_admin', __name__)


@BLUEPRINT.route('/combatant-list', methods=['GET'])
@login_required
def combatant_list():
    """Handle requests to view the user list.

    DataTables will use the combatant API to get combatant data via AJAX

    """
    return render_template('combatant/combatant_list.html')


@BLUEPRINT.route('/combatant-detail/<uuid>', methods=['GET'])
@login_required
def combatant_detail(uuid):
    """Return the combatant detail form.

    Fill it in if a combatant UUID is supplied.

    Args:
        uuid: Optional UUID to fetch combatant data

    """
    if uuid == 'new':
        combatant = None
    else:
        try:
            combatant = Combatant.query.filter(Combatant.uuid == uuid).one()
            logging.debug('editing combatant %s', combatant.sca_name)

        except CombatantDoesNotExist:
            current_app.logger.exception('No combatant with uuid %s', uuid)
            raise

    return render_template(
        'combatant/combatant_detail.html',
        combatant=combatant,
        user=current_user,
        disciplines=Discipline.query.all(),
        # TODO: Take these out when testing is done
        test_card_reminder=add_years(date.today(), -2, 31),
        test_card_expiry=add_years(date.today(), -2, 1),
        test_waiver_reminder=add_years(date.today(), -7, 31),
        test_waiver_expiry=add_years(date.today(), -7, 1)
    )


@BLUEPRINT.route('/combatant-stats', methods=['GET'])
@login_required
def combatant_stats():
    """Display the combatant statistics page."""
    results = {}

    for disc in Discipline.query.all():
        disc_results = []

        # Count the numbers for each authorization
        for auth in disc.authorizations:
            disc_results.append({
                'name': auth.name,
                'count': CombatantAuthorization.query
                    .filter(CombatantAuthorization.authorization_id==auth.id)
                    .count()
            })

        # Count the numbers for each marshal type
        for marshal in disc.marshals:
            disc_results.append({
                'name': marshal.name,
                'count': Warrant.query
                .filter(Warrant.marshal_id==marshal.id)
                .count()
            })

        results[disc.name] = disc_results

    return render_template('user/combatant_stats.html', results=results)
