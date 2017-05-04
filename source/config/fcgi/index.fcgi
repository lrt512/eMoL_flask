#!/home/vagrant/env/bin/python
import sys, os

os.chdir('/var/www/emol')
sys.path.insert(0, os.getcwd())

from flup.server.fcgi import WSGIServer
from emol import app

if __name__ == '__main__':
    WSGIServer(app).run()

