#!/bin/bash
cd /home/app/django

# Manage sync db
python manage.py syncdb --noinput

# manage syncdb migrate
python manage.py migrate

python manage.py loaddata initial_category.json

python manage.py collectstatic --noinput

echo "from django.contrib.auth.models import User; User.objects.create_superuser('cla_admin','peter.idah@digital.justice.gov.uk', 'S3cur31sh')" | ./manage.py shell || echo "user already exists"
