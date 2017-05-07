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
from emol.utility.date import add_years, string_to_date, DATE_FORMAT, LOCAL_TZ

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

    @classmethod
    def create(cls, combatant, waiver_date=None):
        """Create a waiver and schedule its reminders."""
        waiver = cls(combatant_id=combatant.id)
        app.db.session.add(waiver)
        waiver.renew(waiver_date)
        app.db.session.commit()
        return waiver

    def renew(self, waiver_date=None):
        """Renew this waiver.

        Args:
            waiver_date: Optional waiver date, defaults to today.

        """
        # Delete any existing reminders
        self.reminders.clear()

        # Update the card date
        if isinstance(waiver_date, str):
            waiver_date = string_to_date(waiver_date)

        self.waiver = waiver_date or date.today()

        today = datetime.now(LOCAL_TZ).date()

        # Create the reminder for expiry day
        # expiry = (today + relativedelta(years=cls.duration, days=0))
        expiry_date = (today + relativedelta(days=3))
        WaiverReminder.schedule(self, expiry_date, is_expiry=True)

        # Reminders at the specified points before expiry day
        for days in WaiverReminder.reminders:
            reminder_date = expiry_date - relativedelta(days=days)
            WaiverReminder.schedule(self, reminder_date, is_expiry=False)

        app.db.session.commit()

    @property
    def expiry_date(self):
        """Get the waiver expiry date."""
        return add_years(self.waiver, 7)

    @property
    def expiry_date_str(self):
        """Get the combatant's authorization card expiry date as a string."""
        return self.expiry_date.strftime(DATE_FORMAT)

    @property
    def expiry_days(self):
        """Number of days until this card expires."""
        return (self.expiry_date - date.today()).days

    def update(self, waiver_date):
        """Update the waiver date."""
        self.waiver = waiver_date
        app.db.session.commit()


class WaiverReminder(app.db.Model):
    """Waiver expiry reminders for combatants.

    These will be scheduled by Waiver when the waiver
    date(s) are set or changed.

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    reminder_date = app.db.Column(app.db.Date)

    waiver_id = app.db.Column(app.db.Integer, app.db.ForeignKey('waiver.id'))
    waiver = app.db.relationship(
        'Waiver',
        backref = app.db.backref('reminders', cascade='all, delete-orphan')
    )

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
            template = EMAIL_TEMPLATES.get('waiver_reminder')
            subject = template.get('subject')
            body = template.get('body').format(
                expiry_days=self.waiver.expiry_days,
                expiry_date=self.waiver.expiry_date_str
            )

        return Emailer().send_email(self.waiver.combatant.email, subject, body)

    @classmethod
    def schedule(cls, waiver, reminder_date, is_expiry):
        """Schedule waiver expiry reminders for a combatant.

        Args:
            combatant: The combatant to schedule reminders for
        """
        app.logger.debug(
            'schedule waiver {0} for {1}'.format(
                'expiry' if is_expiry else 'reminder',
                reminder_date
            )
        )
        reminder = WaiverReminder(
            reminder_date=reminder_date,
            waiver_id=waiver.id,
            is_expiry=is_expiry
        )
        app.db.session.add(reminder)

    app.db.session.commit()
