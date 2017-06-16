# -*- coding: utf-8 -*-
"""Handlers for user views."""

# standard library imports
from collections import namedtuple

# third-party imports
from flask import Blueprint, render_template, request

# application imports
from emol.decorators import login_required
from emol.models import Combatant, Discipline, CombatantAuthorization, Warrant

BLUEPRINT = Blueprint('user', __name__)

# named tuple for marshal info passed to warrant roster template
MarshalInfo = namedtuple(
    'MarshalInfo',
    ['sca_name', 'legal_name', 'email', 'address', 'phone',
     'member_number', 'member_expiry']
)


@BLUEPRINT.route('/warrant-roster/', methods=['GET', 'POST'])
@login_required
def create_warrant_roster():
    """Warrant roster generation view.

    GET simply displays the warrant roster info collection template:
    - Rex and Regina names (e.g. Henry and Elizabeth)
    - Reign title (e.g. Richard V and Elizabeth I)
    - Coronation data
    - Discipline to generate the roster for
    - ID of the Earl Marshal officer record
    - ID of the deputy kingdom marshal officer record
        (for disciplines other than armoured combat)

    POST uses that info to generate the warrant roster and render it.
    Also sent down is the URI for the discipline's icon/logo so that whoever
    designs the warrant roster template has it available.

    """
    if request.method == 'GET':
        return render_template(
            'user/create_warrant_roster.html',
            disciplines=Discipline.query.all()
        )
    else:
        discipline = Discipline.query.filter(
            Discipline.slug == request.form.get('discipline')).one()
        officer = discipline.officer
        marshal_slugs = [m.slug for m in discipline.marshals]

        marshal_info = []

        for slug in marshal_slugs:
            marshals = Combatant.query.filter(
                # Yes, the values of discipline.slug and slug in the lambda need
                # to be what they are in the current iteration.
                # pylint: disable=cell-var-from-loop
                Combatant.authorizations[discipline.slug][slug] is True
            ).order_by(Combatant.sca_name)

            for marshal in marshals:
                marshal_info.append(MarshalInfo(
                    sca_name=marshal.sca_name,
                    legal_name=marshal.decrypted.get('legal_name'),
                    address=marshal.one_line_address,
                    email=marshal.email,
                    phone=marshal.decrypted.get('phone'),
                    member_number=marshal.decrypted.get('member_number'),
                    member_expiry=marshal.decrypted.get('member_expiry')
                ))

        # return things discretely so that people messing with the template
        # don't need to work with objects and properties
        return render_template(
            'user/warrant_roster.html',
            coronation_date=request.form.get('coronation-date'),
            rex=request.form.get('rex'),
            regina=request.form.get('regina'),
            reign_title=request.form.get('reign-title'),
            discipline=discipline.name,
            icon_path='/static/images/{0}.gif'.format(discipline.slug),
            officer=officer.sca_name,
            officer_title=officer.title,
            parent=officer.parent.sca_name if officer.parent else '',
            parent_title=officer.parent.title if officer.parent else '',
            marshals=marshal_info
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
