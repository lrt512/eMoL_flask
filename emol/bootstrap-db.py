# !/usr/bin/env python

import sys
from subprocess import call
from optparse import OptionParser

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import ImportStringError

parser = OptionParser()
parser.add_option("-f", "--force", action='store_true', dest='overwrite',
                  default=None, help="force overwriting any existing data")

(options, args) = parser.parse_args()
print(options)
overwrite = options.overwrite

if overwrite is None:
    reply = str(input('This will destroy any existing eMoL data and cannot be '
                      'undone. Proceed? (y/N) ')).lower().strip()
    overwrite = reply.lower().strip() == 'y'

if not overwrite:
    sys.exit(-1)

app = Flask(__name__)
try:
    print('Try config from local config.py')
    app.config.from_object('emol.config')
except ImportStringError:
    print('No local config.py, try EMOL_CONFIG environment variable')
    app.config.from_envvar('EMOL_CONFIG')
app.db = SQLAlchemy(app)

# Syscall to create the database
print('Drop any existing database')
call(["mysql", "-uroot", '-pqwert', '-e', 'drop database emol;'])
print('Create database')
call(["mysql", "-uroot", '-pqwert', '-e', 'create database emol;'])
print('\n')

with app.app_context():
    print('Import models')
    from emol.models import *

    print('Create tables')
    app.db.create_all()

    print('Done')
