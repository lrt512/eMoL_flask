"""Deployment support: Deploy eMoL."""
import os

from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists


def deploy_emol(install):
    """Perform the deployment."""
    print('\n\n')
    print(green('Deploying eMoL'))
    package_source()
    unpack_source()
    upload_config()
    write_wsgi()
    create_venv()
    pip_install()
    if install:
        bootstrap_db()
    print('\n')
    # Virtualmin creates user-specific instances of httpd and so mod_wsgi's
    # canonical method of `touch foo.wsgi` to force a reload of the WSGI app
    # does not work (for some reason that I do not actually know).
    # We'll kill the user-specific httpd instance to force reload
    run("kill `ps -u emol | grep apache2 | awk '{ print $1 }'`")
    print(green('Deployment complete'))

# Things that should not get deployed to non-development servers
PACKAGE_EXCLUDES = [
    '.eslintrc',
    '.pylintrc',
    'emol.log',
    'req-development.txt',
    '.cache',
    '__pycache__',
    '*.pyc',
    'tests',
    'less'
]


def package_source():
    """Package up the source files for transfer."""
    print(yellow('Package eMoL source'))
    tar = 'tar'
    for exclude in PACKAGE_EXCLUDES:
        tar += ' --exclude={}'.format(exclude)

    tar += ' -zcf /tmp/emol_source.tgz .'
    local('rm -f /tmp/emol_source.tgz')
    with lcd('/home/vagrant/source/emol'):
        local(tar)
    print(green('Packaging done'))

    print(yellow('Upload source package'))
    put('/tmp/emol_source.tgz', '/tmp')
    print(green('Source upload done'))


def upload_config():
    """Upload the designated config file as config.py"""
    print(yellow('Upload config file'))
    put(
        os.path.join(env.private_directory, env.settings.get('config_file')),
        '/home/emol/emol/emol/config.py'
    )
    print(green('Config uploaded'))


def write_wsgi():
    """Create emol.wsgi in the HTML directory."""
    run(
        'echo "from emol.app import create_app\napplication = create_app()" > {}'
        .format(os.path.join(env.settings.get('http_directory'), 'emol.wsgi'))
    )

def unpack_source():
    """Extract the eMoL source to the public_html directory."""
    run('mkdir -p ~/emol')
    with cd('~/emol'):
        run('tar -xzf /tmp/emol_source.tgz .')


def create_venv():
    """Create the Python virtualenv for eMoL if it does not already exist."""
    print(yellow('Check for eMoL virtualenv'))
    if exists('~/venv/bin/python'):
        print(green('Virtualenv exists'))
        return

    print(yellow('Create eMoL virtualenv'))
    run('python3 -m venv ~/venv')
    print(green('virtualenv done'))


def pip_install():
    """Install required packages with pip."""
    print(yellow('Install Python packages'))
    print(yellow('(pip stdout is suppressed)'))
    with prefix('source ~/venv/bin/activate'):
        with hide('stdout'):
            run('pip install -r ~/emol/req-production.txt')


def bootstrap_db():
    """Create the database."""
    print(yellow('Populate eMoL database'))
    with prefix('source ~/venv/bin/activate'):
        run('~/emol/bootstrap-db.py')
    print(green('eMoL database populated'))
