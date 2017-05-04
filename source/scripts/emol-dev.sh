#!/bin/bash

source ~/env/bin/activate
export EMOL_CONFIG=/home/vagrant/source/config/vagrant/config.py
cd ~/source/emol
python emol.py
