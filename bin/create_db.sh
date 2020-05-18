#!/bin/bash -e

migrations() {
    python manage.py install_postgres_extensions
    python manage.py migrate --noinput

    python manage.py loaddata initial_groups.json
    python manage.py loaddata initial_category.json
    python manage.py loaddata initial_mattertype.json
    python manage.py loaddata initial_media_codes.json
    python manage.py loaddata initial_complaint_categories.json
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
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('$ADMIN_USER', 'civil-legal-advice@digital.justice.gov.uk', '$ADMIN_PASSWORD')" | ./manage.py shell || echo "user already exists"
}

cd /home/app/

migrations
admin_password
load_test_data

exec "$@"
