# -*- coding: utf-8 -*-
"""Model an waiver date."""

# standard library imports
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

# third-party imports
from flask import current_app as app

# application imports
from emol.mail import Emailer
from emol.mail.email_templates import EMAIL_TEMPLATES
from emol.utility.date import add_years, DATE_FORMAT, LOCAL_TZ

__all__ = ['Waiver']


class Waiver(app.db.Model):
    """Model the on-file waiver.

    Attributes:
        id: Primary key in the database
        combatant_id: The combatant's id
        waiver_date: Date the waiver was executed

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    waiver = app.db.Column(app.db.Date)

    combatant_id = app.db.Column(app.db.Integer, app.db.ForeignKey('combatant.id'))
    combatant = app.db.relationship(
        'Combatant',
        backref=app.db.backref('waiver', uselist=False)
    )

    reminders = app.db.relationship('WaiverReminder')

    @property
    def expiry_date(self):
        """Get the combatant's authorization card expiry date.

        That is, the self.waiver + CARD_DURATION years

        Returns:
            Date of the card's expiry date

        """
        return add_years(self.waiver, 2).strftime(DATE_FORMAT)

    def update(self, waiver_date):
        self.waiver = waiver_date
        print(waiver_date)
        app.db.session.commit()


class WaiverReminder(app.db.Model):
    """Waiver expiry reminders for combatants.

    These will be scheduled by Waiver when the waiver
    date(s) are set or changed.

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    reminder_date = app.db.Column(app.db.Date)

    waiver_id = app.db.Column(app.db.Integer, app.db.ForeignKey('waiver.id'))
    waiver = app.db.relationship('Waiver')

    is_expiry = app.db.Column(app.db.Boolean, nullable=False)

    duration = 7
    # reminders = [30, 60]
    reminders = [2, 1]

    def mail(self):
        """Send reminder or expiry email as appropriate to this instance."""

        if self.is_expiry is True:
            template = EMAIL_TEMPLATES.get('waiver_expiry')
            subject = template.get('subject')
            body = template.get('body')
        else:
            template = EMAIL_TEMPLATES.get('waiver_expiry')
            subject = template.get('subject')
            expiry_days = self.waiver.expiry_date - date.today()
            body = template.get('body').format(
                expiry_days.days,
                expiry_date=self.waiver.expiry_date
            )

        return Emailer().send_email(self.combatant.email, subject, body)

    @classmethod
    def schedule(cls, combatant):
        """Schedule card expiry reminders for a combatant.

        Args:
            combatant: The combatant to schedule reminders for
        """
        # Delete existing reminders so we don't spam anyone
        combatant.waiver_reminders.delete()

        today = datetime.now(LOCAL_TZ).date()
        # Check the date as stored in the database, which is N back from today
        # expiry = (today + relativedelta(years=cls.duration, days=0))
        expiry = (today + relativedelta(days=3))
        app.logger.debug('schedule waiver expiry for {1}'.format(expiry))

        # Create the reminder for expiry day
        reminder = cls(
            date=expiry,
            combatant=combatant,
            is_expiry=True
        )
        app.db.session.add(reminder)

        # Reminders at the specified points before expiry day
        for days in cls.reminders:
            reminder = expiry - relativedelta(days=days)
            app.logger.debug('schedule waiver reminder for {1}'.format(reminder))

            # pylint complains about no-member for Pony objects but it's good
            # pylint: disable=no-member
            reminder = cls(
                date=reminder.isoformat(),
                combatant=combatant,
                is_expiry=False
            )
            app.db.session.add(reminder)

        app.db.session.commit()
