# -*- coding: utf-8 -*-
"""Encryption utility class.

This module presents a class that wraps the PyCrypto library to provide
encryption and decryption services for eMoL.

"""

import base64
import json

import boto3
from flask import current_app


class AESCipher(object):
    """Class to encapsulate AES encryption and decryption.

    The path of the file containing the encryption key is passed in to the
    constructor. If eMoL was set up correctly, that file should be readable
    only by the user that eMoL runs under in the httpd/WSGI environment.

    """

    _client = None

    def __init__(self, key):
        """Constructor.

        Verify that the keyfile permissions are correct (TODO), then read the
        key and store it only for the lifetime of this object.

        Args:
            key: The encryption key

        Raises:
            Exception if the keyfile cannot be read
        """
        self._client = boto3.client(
            'kms',
            region_name=current_app.config['AWS_REGION'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )

    def encrypt(self, plaintext):
        """Encrypt the given data then base64 encode.

        Args:
            plaintext: Data to be encrypted

        Returns:
            The encrypted data, base64 encoded
        """
        if plaintext is None:
            return None

        metadata = self._client.encrypt(
            KeyId=current_app.config['EMOL_KMS_KEY'],
            Plaintext=plaintext
        )
        return base64.b64encode(metadata['CiphertextBlob'])

    def decrypt(self, ciphertext):
        """Base64 decode the given ciphertext and then decrypt.

        Args:
            ciphertext: Encrypted data

        Returns:
            The decrypted plaintext
        """
        if ciphertext is None:
            return None

        metadata = self._client.decrypt(
            CiphertextBlob=base64.b64decode(ciphertext)
        )
        return metadata['Plaintext']

    def encrypt_json(self, data):
        """Convert dump data to a JSON string and encrypt.

        Args:
            data: JSON-serializable data

        Returns:
            The encrypted data, base64 encoded

        Raises:
            NameError, TypeError, SyntaxError as json.dumps may raise
        """
        return self.encrypt(json.dumps(data))

    def decrypt_json(self, ciphertext):
        """Decrypt data and deserialize from JSON.

        Args:
            ciphertext: Encrypted JSON-serializable data

        Returns:
            The decrypted data parsed from JSON

        Raises:
            NameError, TypeError, SyntaxError as json.loads may raise
        """
        plaintext = self.decrypt(ciphertext)
        return json.loads(plaintext)
