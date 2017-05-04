# -*- coding: utf-8 -*-
"""Initialize application encryption."""

# standard library imports

# third-party imports
from flask import current_app

# application imports
from emol.exception.encryption_exception import EncryptionException
from emol.utility.setup import is_setup


def init_encryption():
    """Instantiate an encryption object for the app."""
    current_app.logger.info('Initialize encryption')
    from emol.utility.encryption import AESCipher

    def cipher():
        if getattr(current_app, '_cipher', None) is None:
            current_app._cipher = AESCipher(current_app.config.get('KEYFILE_PATH'))

        return current_app._cipher

    current_app.cipher = cipher
