"""Deploy eMoL."""

import os
import sys

from fabric.api import *
from fabric.colors import green, red
import yaml

from deploy_support.test_config import test_config
from deploy_support.deploy import deploy_emol

DEPLOY_DIRECTORY = os.path.dirname(__file__)
env.private_directory= os.path.join(DEPLOY_DIRECTORY, 'private')


def install(destination):
    """Deploy eMoL to the server identified in config_file."""
    destination += '' if destination.lower().endswith('.yaml') else '.yaml'
    path = os.path.join(env.private_directory, destination)

    if not os.path.isfile(path):
        print(red('No such config: {}'.format(destination)))
        sys.exit(-1)

    with open(path, 'r') as stream:
        env.settings = yaml.safe_load(stream)

    print(green('Using config: {}'.format(destination)))

    # Set up env variables
    keyfile_path = os.path.join(env.private_directory, env.settings.get('server_keyfile'))

    env.host_string = env.settings.get('server_hostname')
    env.user = env.settings.get('server_user')
    env.key_filename = keyfile_path

    test_config()
    deploy_emol(install=True)
