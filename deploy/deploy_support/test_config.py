"""Deployment support: Testing the configuration loaded fromYAML."""

import os
import sys

from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.exceptions import NetworkError

from .common import python_3_version

def test_config():
    """Test config and abort on any errors."""
    print(yellow('Testing config...'))
    for test in [test_ssh, test_db, test_python]:
        result = test()
        if result is not None:
            print(red(result))
            sys.exit(1)

    print('\n')
    print(green('Config OK'))


def test_ssh():
    """Verify keyfile existence and test SSH to server."""
    if not env.ssh_key:
        print(yellow('SSH '))
    if not os.path.isfile(env.key_filename):
        return 'Keyfile does not exist'

    print(yellow('Testing SSH connectivity'))
    try:
        run('uname -a')
        print(green('SSH OK'))
        return None
    except NetworkError as exc:
        return str(exc)


def test_db():
    """Test the given database credentials."""
    cmd = ' mysql -u {} -p{} {} -eexit'.format(
        env.settings.get('database_user'),
        env.settings.get('database_password'),
        env.settings.get('database_name'),
    )

    print(yellow('Testing MySQL connectivity'))
    with settings(warn_only=True):
        result = run(cmd)
        if result.return_code == 0:
            print(green('Database OK'))
            return None

        return result


def test_python():
    """Make sure Python 3.6 is present."""
    print(yellow('Ensure Python 3.6 is present'))

    with settings(warn_only=True):
        major, minor = python_3_version()

        if minor is None or minor < 6:
            print(red('No Python >= 3.6 is installed'))
        else:
            print(green('Python {}.{} OK').format(major, minor))
            return None
