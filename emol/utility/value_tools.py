# -*- coding: utf-8 -*-
"""Utility functions for combatant import."""


def is_blank(value):
    """Check for blankness.

    Args:
        value: The value to check

    Returns:
        True if value is an empty string, not a string, etc.
        False if value is a non-empty string

    """
    if value is None:
        return True

    if isinstance(value, str) is False:
        return True

    # Empty strings return False
    if not value.strip():
        return True

    return False


def not_blank(value):
    """Check for not-blankness.

    Args:
        value: The value to check

    Returns:
        False if value is an empty string, not a string, etc.
        True if value is a non-empty string

    """
    return not is_blank(value)


def yes_or_no(value):
    """Map the to a boolean True/False.

    - Blank values are False
    - 'yes' or 'y' are True
    - 'on' is True

    Args:
        value: The value to check

    Returns:
        True if value is yes (case-insensitive)
        False otherwise

    """
    if value is True:
        return True

    if is_blank(value):
        return False

    if value.strip().lower() == 'yes':
        return True

    if value.strip().lower() == 'y':
        return True

    if value.strip().lower() == 'on':
        return True

    return False
