#!/usr/bin/env python

import os
import sys
from subprocess import call

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
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
