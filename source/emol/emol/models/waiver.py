# -*- coding: utf-8 -*-
"""Model an waiver date."""

# standard library imports
from dateutil.relativedelta import relativedelta

# third-party imports
from flask import current_app as app

# application imports
from emol.mail import Emailer
from emol.mail.email_templates import EMAIL_TEMPLATES
from emol.utility.date import add_years, string_to_date, today, DATE_FORMAT, LOCAL_TZ

from .config import Config

__all__ = ['Waiver']


class Waiver(app.db.Model):
    """Model the on-file waiver.

    Attributes:
        id: Primary key in the database
        combatant_id: The combatant's id
        waiver_date: Date the waiver was executed

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    waiver_date = app.db.Column(app.db.Date)

    combatant_id = app.db.Column(app.db.Integer, app.db.ForeignKey('combatant.id'))

    reminders = app.db.relationship(
        'WaiverReminder', backref = 'waiver',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return 'Waiver: {0.email} ({0.id})'.format(self.combatant)

    @classmethod
    def create(cls, combatant, waiver_date=None):
        """Create a waiver and renew it.

        Args:
            combatant: The combatant this waiver is for
            waiver_date: Date the waiver was executed

        """
        waiver = Waiver(combatant=combatant)
        app.db.session.add(waiver)
        waiver.renew(waiver_date)
        return waiver

    def renew(self, waiver_date=None):
        """Renew this waiver.

        Args:
            waiver_date: Optional waiver date, defaults to today.

        """
        # Delete any existing reminders
        WaiverReminder.query.filter(
            WaiverReminder.waiver_id == self.id
        ).delete()

        # Update the card date
        if isinstance(waiver_date, str):
            waiver_date = string_to_date(waiver_date)

        self.waiver_date = waiver_date or today()

        # Create the reminder for expiry day
        expiry_date = self.waiver_date + relativedelta(years=7)
        WaiverReminder.schedule(self, expiry_date, is_expiry=True)

        # Reminders at the specified points before expiry day
        for days in Config.get('waiver_reminders'):
            reminder_date = expiry_date - relativedelta(days=days)
            WaiverReminder.schedule(self, reminder_date, is_expiry=False)

        app.db.session.commit()

    @property
    def expiry_date(self):
        """Get the waiver expiry date."""
        return add_years(self.waiver_date, 7)

    @property
    def expiry_date_str(self):
        """Get the combatant's authorization card expiry date as a string."""
        return self.expiry_date.strftime(DATE_FORMAT)

    @property
    def expiry_days(self):
        """Number of days until this card expires."""
        return (self.expiry_date - today()).days


class WaiverReminder(app.db.Model):
    """Waiver expiry reminders for combatants.

    These are scheduled by Waiver when the waiver date(s) are set or changed.

    Attributes:
        id: Primary key
        reminder_date: Date that the reminder should be sent
        waiver_id: ID of the waiver this reminder is associated to
        is_expiry: True if this reminder will send an expiry notice

    Backrefs:
        combatant: Via Combatant.waiver

    """

    id = app.db.Column(app.db.Integer, primary_key=True)
    reminder_date = app.db.Column(app.db.Date)

    waiver_id = app.db.Column(app.db.Integer, app.db.ForeignKey('waiver.id'))

    is_expiry = app.db.Column(app.db.Boolean, nullable=False)

    def __repr__(self):
        return 'WaiverReminder: {0} ({1})'.format(
            self.waiver.combatant_id,
            self.reminder_date
        )

    def mail(self):
        """Send reminder or expiry notice as appropriate."""

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
        """Schedule a waiver expiry reminder for a combatant.

        Args:
            combatant: The combatant to schedule reminders for
            reminder_date: The date for the reminder
            is_expiry: True if the reminder will be an expiry notice

        """
        app.logger.debug(
            'schedule waiver {0} for {1} ({2}): {3}'.format(
                'expiry' if is_expiry else 'reminder',
                waiver.combatant.email,
                waiver.combatant_id,
                reminder_date
            )
        )
        reminder = WaiverReminder(
            reminder_date=reminder_date,
            waiver=waiver,
            is_expiry=is_expiry
        )
        app.db.session.add(reminder)
        app.db.session.commit()
