# -*- coding: utf-8 -*-
"""Database utility functions."""

# standard library imports
import uuid


def default_uuid():
    """Because SQLA is a bit daft about UUIDs."""
    return uuid.uuid4().hex
