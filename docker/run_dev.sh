#!/usr/bin/env bash
set -e
# Generate SSH host keys (fix for the error)
ssh-keygen -A
/usr/sbin/sshd

# used to generate static files for local development.

su -c 'python manage.py collectstatic --noinput' app

su -c './manage.py runserver 0.0.0.0:8000' app
