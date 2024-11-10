#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
# pip install virtualenv
# virtualenv env
# source env/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --no-input
# deactivate
# rm -rf env/