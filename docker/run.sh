#!/usr/bin/env bash
set -e

# Run server
export WORKER_APP_CONCURRENCY=${WORKER_APP_CONCURRENCY:-8}
uwsgi --ini /home/app/docker/cla_backend.ini
