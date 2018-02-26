"""Deployment support: Testing the configuration loaded fromYAML."""

import os
import re
import sys

from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.exceptions import NetworkError


def python_3_version():
    """See what version of python 3 is present.
    Returns:
        (major, minor) of the installed Python 3 version, if Python 3 is
        installed, if any.
        None if no version of Python3 is installed.
    """
    with settings(warn_only=True):
        out = run('python3.6 --version')
        if out.return_code == 0:
            env.python_version = 3.6
            return 3, 6

        out = run('python3 --version')
        match = re.search('Python 3.(?P<minor>\d)', out)
        if match is not None:
            minor = match.group('minor')
            env.python_version = float('3.{}'.format(minor))
            return 3, int(minor)

        env.python_version = None
        return None, None


def mysql_version():
    """See what version of MySQL is present.

    Returns:
        (major, minor) of the installed MySQL server, if any.
        None if no version of MySQL server is installed.
    """
    out = run('dpkg -l | grep -E "mysql-server\s+"')
    match = re.search('mysql-server\s+(?P<major>\d)\.(?P<minor>\d+)', out.strip())
    if match is None:
        return None, None
        env.mysql_version = None

    major = int(match.group('major'))
    minor = int(match.group('minor'))

    env.mysql_version = float('{}.{}'.format(major, minor))
    return major, minor
