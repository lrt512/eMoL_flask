"""Deploy eMoL."""

import os
import sys

from fabric.api import *
from fabric.colors import green, red
import yaml

from deploy_support.test_config import test_config
from deploy_support.configure_server import install_db, install_python
from deploy_support.deploy import deploy_emol

DEPLOY_DIRECTORY = os.path.dirname(__file__)


def configure(destination):
    """Read the config file specified and set up the fabric environment."""
    if all([env.host_string, env.user, env.key_filename]):
        return

    path_ = os.path.join(DEPLOY_DIRECTORY, destination)
    if not os.path.exists(path_):
        print(red('No such config: {}'.format(destination)))
        sys.exit(-1)

    config_file = os.path.join(path_, 'deploy.yaml')
    with open(config_file, 'r') as stream:
        env.settings = yaml.safe_load(stream)

    print(green('Using config: {}'.format(destination)))

    # Set up env variables
    env.destination = destination
    env.host_string = env.settings.get('server_hostname')
    env.user = env.settings.get('server_user')

    # SSH key if provided
    env.ssh_key = False
    keyfile_path = os.path.join(path_, 'ssh.key')
    if os.path.exists(keyfile_path):
        env.ssh_key = True
        env.key_filename = keyfile_path


def full_install(destination):
    configure(destination)
    vagrant()
    prepare_server(destination)


def vagrant():
    """Vagrant up if this is a Vagrant-based deployment."""
    env.vagrant = env.settings.get('vagrant', False)
    if vagrant:
        print(green('Executing vagrant up'))

        with lcd(env.destination):
            result = local('vagrant up')
            if result:
                print(red('Vagrant failed, aborting.'))
                sys.exit(-1)


def prepare_server(destination):
    """Set up the eMoL deployment environment."""
    configure(destination)
    install_db()
    install_python()


def install(destination):
    """Deploy eMoL to the server identified in config_file."""
    configure(destination)
    test_config()
    deploy_emol(install=True)
