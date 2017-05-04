# -*- coding: utf-8 -*-
"""Encryption utility class.

This module presents a class that wraps the pyaes library to provide encryption
 and decryption services for eMoL.

"""

# standard library imports
import json
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


# application imports
from emol.exception.encryption_exception import EncryptionException


class AESCipher(object):
    """Class to encapsulate AES encryption and decryption.

    The path of the file containing the encryption key is passed in to the
    constructor. If eMoL was set up correctly, that file should be readable
    only by the user that eMoL runs under in the httpd/WSGI environment.

    """

    _key = None
    _block_size = 16

    def __init__(self, keyfile):
        """Constructor.

        Verify that the keyfile permissions are correct (TODO), then read the
        key and store it only for the lifetime of this object.

        Args:
            keyfile: String containing the path to the keyfile

        Raises:
            Exception if the keyfile cannot be read
        """
        # TODO: Verify keyfile permissions and complain if they are bad

        try:
            with open(keyfile) as keyfile_file:
                self._key = bytes(keyfile_file.read().strip(), 'UTF-8')
        # TODO: Use custom exceptions
        except Exception:
            raise EncryptionException('cannot read keyfile {0}'.format(keyfile))

    def _pad(self, s):
        bs = AES.block_size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def encrypt(self, plaintext):
        """Encrypt the given data then base64 encode.

        Args:
            plaintext: Data to be encrypted

        Returns:
            The encrypted data, base64 encoded
        """
        if plaintext is None:
            return None

        raw = self._pad(plaintext)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, ciphertext):
        """Base64 decode the given ciphertext and then decrypt.

        Args:
            ciphertext: Encrypted data

        Returns:
            The decrypted plaintext
        """
        if ciphertext is None:
            return None

        enc = base64.b64decode(ciphertext)
        iv = enc[:AES.block_size]
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

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
