#!/usr/bin/env bash

brew install python
easy_install pip
pip install --upgrade setuptools --user python
pip install paramiko --user
pip install colorama --user
pip install termcolor --user
pip install pyfiglet --user

python setup.py install