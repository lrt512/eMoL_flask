import json
import os
import tempfile
import uuid

import pytest

from emol.utility.encryption import AESCipher

KEY_SIZE = 256
PLAINTEXT = '01234567890123456'


@pytest.fixture(scope='function')
def cipher():
    """Generate a keyfile and a cipher that uses it."""
    _, path = tempfile.mkstemp()

    with open(path, 'w') as f:
        key = uuid.uuid4().hex[:KEY_SIZE // 8]
        f.write(key)

    cipher = AESCipher(path)

    yield cipher

    os.unlink(path)


@pytest.fixture(scope='function')
def cipher2(cipher):
    """Generate a keyfile and a cipher that uses it."""
    _, path = tempfile.mkstemp()

    with open(path, 'w') as f:
        key = uuid.uuid4().hex[:KEY_SIZE // 8]
        f.write(key)

    cipher = AESCipher(path)

    yield cipher

    os.unlink(path)


def test_encrypt_decrypt(cipher):
    """Basic encrypt and decrypt test"""
    ciphertext = cipher.encrypt(PLAINTEXT)
    decrypted = cipher.decrypt(ciphertext)
    assert decrypted == PLAINTEXT


def test_encrypt_json(cipher):
    """Basic encrypt and decrypt JSON test"""
    data = dict(foo='bar', baz=True, quux=7)
    json_data = json.dumps(data)

    ciphertext = cipher.encrypt_json(data)
    decrypted = cipher.decrypt_json(ciphertext)

    decrypted_json = json.dumps(decrypted)
    assert decrypted_json == json_data
    assert decrypted == data


def test_encrypt_wrong_key(cipher, cipher2):
    """Encrypt with one key, decrypt with another. This had better fail."""
    ciphertext = cipher.encrypt(PLAINTEXT)
    try:
        decrypted = cipher2.decrypt(ciphertext)
        assert decrypted != PLAINTEXT
    except UnicodeDecodeError:
        assert True
