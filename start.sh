#!/bin/bash

pip3 install virtualenv
virtualenv nftprojectenv
source nftprojectenv/bin/activate
cd nft_project
pip install -r requirements.txt
python manage.py runserver
