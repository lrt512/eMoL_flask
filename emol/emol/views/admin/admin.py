# -*- coding: utf-8 -*-
"""Administration views."""

# standard library imports
# import csv

# third-party imports
from flask import Blueprint, render_template, request

# application imports
from emol.decorators import admin_required
from emol.models import Discipline

BLUEPRINT = Blueprint('admin', __name__)


@admin_required
@BLUEPRINT.route('/import')
def import_combatants():
    """Mass import handler."""
    if request.method == 'GET':
        return render_template(
            'admin/import.html',
            disciplines=Discipline.query.all()
        )

    elif request.method == 'POST':
        pass
        # shutup pylint
        # reader = csv.DictReader(
        #     request.POST.get('import_file').file,
        #     delimiter=',',
        #     quotechar='"'
        # )

        # read = 0
        # created = 0

        # for row in reader:
        #     read += 1
        #     combatant = Combatant.create_or_update(row)
        #     if combatant is not None:
        #         created += 1
