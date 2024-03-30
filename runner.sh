#!/bin/bash

pip install --upgrade pip

echo 'Collecting static files...'
python manage.py collectstatic --no-input

echo 'Make migrations...'
python manage.py makemigrations --no-input
python manage.py migrate --no-input
echo 'done migrations.'

echo 'Running server...'
daphne -p 8000 server.asgi:application
