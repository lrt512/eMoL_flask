# -*- coding: utf-8 -*-
"""Initialize application encryption."""

from flask import current_app


def init_encryption():
    """Instantiate an encryption object for the app."""
    current_app.logger.info('Initialize encryption')
    from emol.utility.encryption import AESCipher

    def cipher():
        if getattr(current_app, '_cipher', None) is None:
            key = current_app.config.get('SECRET_KEY')
            current_app._cipher = AESCipher(key)

        return current_app._cipher

    current_app.cipher = cipher
