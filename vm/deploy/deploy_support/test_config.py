"""Deployment support: Testing the configuration loaded fromYAML."""

import os
import sys

from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.exceptions import NetworkError


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
    """Check for Python 3.5+ and virtualenv on the server."""
    print(yellow('Check specified Python version'))
    put(
        os.path.join(
            os.path.dirname(__file__),
            'upload',
            'check_version.py'
        ),
        '/tmp'
    )

    with settings(warn_only=True):
        result = run('python3 /tmp/check_version.py')
        run('rm /tmp/check_version.py')
        if result.return_code == 0:
            print(green('Python OK'))
            return None

        return "eMoL requires Python 3.6 or higher"
