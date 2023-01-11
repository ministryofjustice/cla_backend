#!/usr/bin/env bash
set -e

# used to generate static files for local development.

python manage.py collectstatic --noinput

# Run server
python manage.py runserver 8000
