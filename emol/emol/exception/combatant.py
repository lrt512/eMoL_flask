# -*- coding: utf-8 -*-
"""Combatant exceptions."""


class CombatantDoesNotExist(BaseException):
    """Combatant not found exception."""

    def __init__(self, email):
        """Constructor.

        Initialize the exception with a message based on combatant email.

        """
        super().__init__(
            'A combatant with email "{0}" could not be found'.format(email)
        )
