#!/usr/bin/env bash
set -e
cd frontend
npm install
npm run build
cd ../backend
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
