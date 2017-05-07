# -*- coding: utf-8 -*-
"""Emailer class.

Provides an emailing facility that works with email templates as defined in
email_templates.py.

"""

# standard library imports
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate
from uuid import uuid4

# third-party imports
from flask import current_app

# application imports
from emol.exception.privacy_acceptance import PrivacyPolicyNotAccepted
from emol.mail.email_templates import EMAIL_TEMPLATES


class Emailer(object):
    """An application-specific emailer.

    Templates are defined in email_templates.py and each has an associated
    send_xxx staticmethod.

    SMTP configuration in config.py:
        MAIL_HOST = <your SMTP server>
        MAIL_PORT = <defaults to 25 if omitted>
        MAIL_USERNAME = <SMTP user>
        MAIL_PASSWORD = <SMTP password>
        MAIL_DEFAULT_SENDER = 'eMoL <emol@example.com>'
        MAIL_USE_SSL = True/False
        MAIL_USE_TLS = True/False

    """

    @classmethod
    def send_email(cls, recipient, subject, body):
        """Send an email.

        Args:
            recipient: Recipient's email address
            subject: The email's subject
            body: Email message text

        Returns:
            True if the message was delivered

        """
        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = recipient
        message['Message-ID'] = make_msgid(uuid4().hex)
        message['Date'] = formatdate(localtime=True)
        message.attach(MIMEText(body, 'plain'))

        if current_app.config.get('SEND_EMAIL', True) is False:
            current_app.logger.debug('Not sending email')
            current_app.logger.debug(message)
            return True

        smtp = smtplib.SMTP(
            current_app.config.get('MAIL_HOST'),
            current_app.config.get('MAIL_PORT', 25)
        )
        try:
            login = current_app.config.get('MAIL_USERNAME')
            password = current_app.config.get('MAIL_PASSWORD')
            if login is not None and password is not None:
                smtp.login(login, password)

            smtp.sendmail(sender, [recipient], message.as_string())
            return True
        except (socket.error, smtplib.SMTPException):
            current_app.logger.exception('Error sending email')
            return False
        finally:
            smtp.quit()

    @classmethod
    def send_waiver_expiry(cls, combatant, expiry_days):
        """Send a waiver expiry notice to a combatant.

        Args:
            combatant: The combatant being notified
            expiry_days: Number of days in advance to check

        """
        template = EMAIL_TEMPLATES.get('waiver_expiry')
        body = template.get('body').format(
            expiry_days=expiry_days,
            expiry_date=combatant.waiver_expiry
        )
        return cls.send_email(combatant.email, template.get('subject'), body)

    @classmethod
    def send_card_reminder(cls, combatant, expiry_days):
        """Send a card reminder notice to a combatant.

        Args:
            combatant: The combatant being notified
            expiry_days: Number of days in advance to check

        """
        template = EMAIL_TEMPLATES.get('card_expiry')
        body = template.get('body').format(
            expiry_days=expiry_days,
            expiry_date=combatant.card_expiry
        )
        return cls.send_email(combatant.email, template.get('subject'), body)

    @classmethod
    def send_waiver_reminder(cls, combatant, expiry_days):
        """Send a waiver reminder notice to a combatant.

        Args:
            combatant: The combatant being notified
            expiry_days: Number of days in advance to check

        """
        template = EMAIL_TEMPLATES.get('waiver_expiry')
        body = template.get('body').format(
            expiry_days=expiry_days,
            expiry_date=combatant.waiver_expiry
        )
        return cls.send_email(combatant.email, template.get('subject'), body)

    @classmethod
    def send_info_update(cls, combatant, update_request):
        """Send a information update link to a combatant.

        Args:
            combatant: The combatant to send notice to
            update_request: The update request

        """
        template = EMAIL_TEMPLATES.get('info_update')
        body = template.get('body').format(
            update_url=update_request.change_info_url
        )
        return cls.send_email(combatant.email, template.get('subject'), body)

    @classmethod
    def send_card_request(cls, combatant):
        """Send a combatant their card URL.

        Args:
            combatant: The combatant to send notice to

        Raises:
            PrivacyAcceptance.NotAccepted if the combatant has not
                yet accepted the privacy policy

        """
        try:
            template = EMAIL_TEMPLATES.get('card_request')
            body = template.get('body').format(
                card_url=combatant.card_url
            )
            return cls.send_email(
                combatant.email,
                template.get('subject'),
                body
            )
        except PrivacyPolicyNotAccepted:
            current_app.logger.exception(
                'Attempt to send card URL to {0} (privacy not accepted)'
                .format(combatant.email)
            )
            raise

    @classmethod
    def send_privacy_policy_acceptance(cls, privacy_acceptance):
        """Send the privacy policy email to a combatant.

        Use the given PrivacyAcceptance record to get the email address and
        dispatch the email.

        Args:
            privacy_acceptance: A PrivacyAcceptance object to work from

        """
        template = EMAIL_TEMPLATES.get('privacy_policy')
        body = template.get('body').format(
            privacy_policy_url=privacy_acceptance.privacy_policy_url
        )
        return cls.send_email(
            privacy_acceptance.combatant.email,
            template.get('subject'),
            body
        )
