# -*- coding: utf-8 -*-
"""Encryption exceptions."""


class EncryptionException(Exception):
    """General exception during encryption."""

    def __init__(self, message):
        """Constructor setting generic message."""
        super().__init__(message)
