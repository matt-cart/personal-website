#!/bin/bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python create_database.py
cd website/static/
bower install
cd ../..
