#!/usr/bin/env bash
set -e

# used to generate static files for local development.
if [ $STATIC_FILES_BACKEND != "s3" ]
then
  python manage.py collectstatic --noinput
fi
# Run server
python manage.py runserver 8000
