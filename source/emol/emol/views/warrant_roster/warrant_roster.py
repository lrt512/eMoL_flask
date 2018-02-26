# -*- coding: utf-8 -*-
"""Handlers for user views."""

# standard library imports
from collections import namedtuple

# third-party imports
from flask import Blueprint, render_template, request

# application imports
from emol.decorators import login_required
from emol.models import Combatant, Discipline, CombatantAuthorization, Warrant

BLUEPRINT = Blueprint('warrant_roster', __name__)

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
            'warrant_roster/create_warrant_roster.html',
            disciplines=Discipline.query.all()
        )
    else:
        discipline = Discipline.query.filter(
            Discipline.slug == request.form.get('discipline')).one()
        officer = discipline.officer

        marshal_info = []

        for marshal in discipline.marshals:
            warrants = Warrant.query.filter(
                Warrant.marshal_id == marshal.id
            ).all()

            for warrant in warrants:
                combatant = warrant.card.combatant
                print(combatant)
                marshal_info.append(MarshalInfo(
                    sca_name=combatant.sca_name,
                    legal_name=combatant.decrypted.get('legal_name'),
                    address=combatant.one_line_address,
                    email=combatant.email,
                    phone=combatant.decrypted.get('phone'),
                    member_number=combatant.decrypted.get('member_number'),
                    member_expiry=combatant.decrypted.get('member_expiry')
                ))

        # return things discretely so that people messing with the template
        # don't need to work with objects and properties
        return render_template(
            'warrant_roster/warrant_roster.html',
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
