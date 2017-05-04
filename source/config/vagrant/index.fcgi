#!/home/vagrant/env/bin/python
import sys, os

os.chdir('/var/www/emol')
sys.path.insert(0, os.getcwd())

os.environ['EMOL_CONFIG'] = '/home/vagrant/source/config/vagrant/config.py'

from flup.server.fcgi import WSGIServer
from emol.app import app

if __name__ == '__main__':
    WSGIServer(app).run()

