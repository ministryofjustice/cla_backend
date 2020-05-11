#!/bin/bash -e

sentry_config() {
! $([[  "$CLA_ENV" == "prod" || "$CLA_ENV" == "staging" ]]) ||
    grep sentry /etc/hosts > /dev/null 2>&1 ||
    echo "$SENTRY_IPADDRESS $SENTRY_HOSTNAME" >> /etc/hosts
}

migrations() {
    if [ "$BACKEND_ENABLED" == "True" ]; then

        python manage.py install_postgres_extensions
        python manage.py migrate --noinput

        python manage.py loaddata initial_groups.json
        python manage.py loaddata initial_category.json
        python manage.py loaddata initial_mattertype.json
        python manage.py loaddata initial_media_codes.json
        python manage.py loaddata initial_complaint_categories.json

    fi
}

load_test_data() {
    if [ "$LOAD_TEST_DATA" == "True" ]; then

        python manage.py loaddata test_provider.json
        python manage.py loaddata test_provider_allocations.json
        python manage.py loaddata test_auth_clients.json
        python manage.py loaddata test_rotas.json

    fi
}

admin_password() {
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('cla_admin', 'jags.parbha@digital.justice.gov.uk', '$ADMIN_PASSWORD')" | ./manage.py shell || echo "user already exists"
}

cd /home/app

# sentry_config
 migrations
# admin_password
 load_test_data

exec "$@"
