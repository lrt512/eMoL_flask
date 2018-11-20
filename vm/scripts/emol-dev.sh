#!/bin/bash

source ~/env/bin/activate
export EMOL_CONFIG=/home/vagrant/source/config/vagrant/config.py
cd ~/source/emol
flask run -h 0.0.0.0 --debugger --reload
