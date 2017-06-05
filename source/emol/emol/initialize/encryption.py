# -*- coding: utf-8 -*-
"""Initialize application encryption."""

# standard library imports
import os

# third-party imports
from flask import current_app

# application imports
from emol.exception.encryption_exception import EncryptionException
from emol.utility.setup import is_setup


def init_encryption():
    """Instantiate an encryption object for the app."""
    current_app.logger.info('Initialize encryption')
    from emol.utility.encryption import AESCipher

    keyfile_dir = os.path.dirname(current_app.config.get('KEYFILE_PATH'))

    if not os.path.isdir(keyfile_dir):
        current_app.logger.info('Create keyfile directory')
        os.makedirs(keyfile_dir)
        os.chmod(keyfile_dir, 0o700)


    def cipher():
        if getattr(current_app, '_cipher', None) is None:
            current_app._cipher = AESCipher(current_app.config.get('KEYFILE_PATH'))

        return current_app._cipher

    current_app.cipher = cipher
