#!/usr/bin/env bash
set -e

# used to generate static files for local development.
if [ $STATIC_FILES_BACKEND != "s3" ]
then
  python manage.py collectstatic --noinput
fi
# Run server
export WORKER_APP_CONCURRENCY=${WORKER_APP_CONCURRENCY:-8}
uwsgi --ini /home/app/docker/cla_backend.ini
