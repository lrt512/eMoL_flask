"""Utilities for unit testing."""

from importlib import __import__
import pytest
import sys


class Mocktoday(object):
    """A context manager for to fake out datetime.date.today.

    Monkeypatches the given module to swap out today with our
    own function so that we can say that "today" is any date we want.

    This assumes you're using emol.utility.date.today and not date.today()
    (the latter is a proxy for the former to facilitate this thing)

    Usage:

       from utils import Mocktoday

       def test_party_like_its_1999():
          with Mocktoday('emol.this.that', date(1999, 01, 01))
             # do something that will call today()

    """

    def mock_today(self):
        """Replacement for today function for unit tests."""
        return self.desired_date

    def __init__(self, module, desired_date):
        """Constructor.

        Args:
           module: The module name to operate on
           desired_date: The date to report

        """
        self.module = sys.modules[module]
        self.desired_date = desired_date

        # Swap out the module's imported today function
        self.orig = self.module.today
        self.module.today = self.mock_today

    def __enter__(self, *args, **kwargs):
        """Nothing to do here."""
        pass

    def __exit__(self, *args, **kwargs):
        """Reset the proper today function."""
        self.module.today = self.orig



class Mockmail(object):
    """A context manager for mail.Emailer unit testing.

    Monkeypatches the given module to swap out Emailer with a testing class
    so that we can test whether or not any of the email sending methods were
    called by an invocation.

    Usage (from a model unit test):

       from emol.utility.testing import Mockmail

       def test_something_that_sends_mail():
          with Mockmail('emol.this.that', True)
             # do something that should cause send_email to be called

       def test_something_that_does_not_mail():
          with Mockmail('emol.this.that', False)
             # do something that should not cause send_email to be called

    """

    messages = {
        True: 'Expected send_email to be called but it was not',
        False: 'Expected send_email to not be called but it was'
    }

    def __init__(self, module, expected_result):
        """Constructor.

        Args:
           module: The module name to operate on
           expected_result: True if a call that sends email is expected,
                            False if not. None for no test (fixtures)

        """

        class TestEmailer(object):
            """Unit testing replacement for mail.Emailer.

            Override all the methods below to just set self.mocked on
            the enclosing Mockmail.

            """

            @classmethod
            def send_email(cls, a, b, c):
                self.mocked = True

            @classmethod
            def send_waiver_expiry(cls, combatant, expiry_days):
                self.mocked = True

            @classmethod
            def send_card_reminder(cls, combatant, expiry_days):
                self.mocked = True

            @classmethod
            def send_waiver_reminder(cls, combatant, expiry_days):
                self.mocked = True

            @classmethod
            def send_info_update(cls, combatant, update_request):
                self.mocked = True

            @classmethod
            def send_card_request(cls, combatant):
                self.mocked = True

            @classmethod
            def send_privacy_policy_acceptance(cls, privacy_acceptance):
                self.mocked = True

        self.expected_result = expected_result
        self.module = sys.modules[module]

        # Swap out the module's Emailer loaded from emol.mail
        self.orig = self.module.Emailer
        self.module.Emailer = TestEmailer

    def __enter__(self):
        """Reset self.mocked."""
        self.mocked = False

    def __exit__(self, *args, **kwargs):
        """Reset the proper send_email method and assess the result."""
        self.module.Emailer = self.orig

        if self.expected_result is None:
            return

        if self.mocked != self.expected_result:
            pytest.fail(self.messages[self.expected_result])
