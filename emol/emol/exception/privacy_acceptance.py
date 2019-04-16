# -*- coding: utf-8 -*-
"""Privacy policy acceptance exceptions."""


class PrivacyPolicyNotAccepted(Exception):
    """Privacy policy not accepted exception."""

    def __init__(self):
        """Constructor setting generic message."""
        super().__init__(
            'This combatant has not yet accepted the privacy policy. '
            'Until then, eMoL functionality is unavailable'
        )
