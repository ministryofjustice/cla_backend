#!/usr/bin/env bash
set -e

# used to generate static files for local development.

python manage.py collectstatic --noinput

./manage.py runserver 0.0.0.0:8000
