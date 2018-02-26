"""Deployment support: Testing the configuration loaded fromYAML."""

import os
import re
import sys

from fabric.api import *
from fabric.colors import green, red, yellow

from .common import python_3_version, mysql_version


def install_db():
    """Make sure MySQL 5 is present."""
    print(yellow('Ensure MySQL is installed'))
    with settings(warn_only=True):
        major, minor = mysql_version()

        if major is None or major < 5:
            sudo('apt-get install -y mysql-server')
            mysql_version()

        print(green('MySQL {} present'.format(env.mysql_version)))


def install_python():
    """Make sure Python 3.6 is present."""
    print(yellow('Ensure Python 3.6+ is present'))
    with settings(warn_only=True):
        major, minor = python_3_version()

        if major is None or minor < 6:
            print(yellow('Installing Python 3.6'))
            sudo('add-apt-repository -y ppa:jonathonf/python-3.6')
            sudo('apt-get update')
            sudo('apt-get install -y python3.6')
            python_3_version()

        print(green('Python {} present'.format(env.python_version)))
