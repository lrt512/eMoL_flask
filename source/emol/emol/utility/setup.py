# -*- coding: utf-8 -*-
"""Utility functions for eMoL setup."""

# standard library imports
import os

# third-party imports
from flask import current_app

# application imports

def test_encryption_key(key_file):
    """Test keyfile security.

    Make sure that eMoL has permission to read and write the keyfile directory
    and the keyfile itself.

    Also ensure that the keyfile directory has 0700 permissions

    Args:
        key_file:

    Returns: A dictionary with
        ok: Whether the keyfile itself exists or not
        results: a dict with a boolean status and a message

    """
    results = []

    key_dir = os.path.dirname(key_file)

    if os.path.exists(key_dir) is False:
        results.append({
            'status': False,
            'message': 'Keyfile directory does not exist'
        })
        return {'ok': False, 'results': results}

    results.append({'status': True, 'message': 'Keyfile directory exists'})
    keyfile_ok = True

    key_dir_mode = os.stat(key_dir).st_mode & 0o777

    if key_dir_mode == 0o700:
        results.append({
            'status': True,
            'message': 'Keyfile directory permissions are OK'
        })
    else:
        results.append({
            'status': False,
            'message': 'Keyfile directory permissions are not 0700'
        })

    keyfile_ok &= key_dir_mode == 0o700

    return {'ok': keyfile_ok, 'results': results}


def is_setup():
    """Simple check to see if eMoL is already set up.

    Check for existence of the database file and then check to see if
    the config table exists

    Returns:
        True if the config table exists and has at least one row
    """
    from emol.models import Config

    try:
        return Config.get('is_setup') is True
    except:
        return False
