# -*- coding: utf-8 -*-
"""API endpoint for combatant import."""

# standard library imports
import csv
from io import TextIOWrapper

# third-party imports
from flask import request, abort, current_app
from flask_restful import Resource

# application imports
from emol.models import Combatant, Discipline
from emol.utility.value_tools import yes_or_no
from emol.utility.date import add_years, string_to_date


@current_app.api.route('/api/import')
class ImportApi(Resource):
    """Endpoint for combatant import.

    Permitted methods: POST

    Allows for upload of a CSV file full of combatant data

    """

    @staticmethod
    def post():
        """Import some combatants."""
        slug = request.form['discipline']
        discipline = Discipline.find(slug)

        combatant_data = request.files['file']
        f = TextIOWrapper(combatant_data, encoding='utf-8')
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            try:
                combatant = Combatant.create(row)
                current_app.logger.info('Import {}'.format(combatant))
                card = combatant.get_card(discipline, create=True)

                card_date = row.get('card_date')
                if card_date is None:
                    card.card_date = None
                else:
                    card.card_date = add_years(card_date, -2)

                for auth in discipline.authorizations:
                    if yes_or_no(row.get(auth.slug)):
                        card.add_authorization(auth)
                    else:
                        card.remove_authorization(auth)

                if row.get('member_number') and row.get('member_expiry'):
                    for marshal in discipline.marshals:
                        if yes_or_no(row.get(marshal.slug)):
                            card.add_warrant(marshal)
                        else:
                            card.remove_warrant(marshal)
            except Exception as exc:
                current_app.logger.exception(exc)
