#!/usr/bin/env bash
set -e

# Run server
if [ $STATIC_FILES_BACKEND != "s3" ]
then
  python manage.py collectstatic --noinput
fi

export WORKER_APP_CONCURRENCY=${WORKER_APP_CONCURRENCY:-8}
uwsgi --ini /home/app/docker/cla_backend.ini
