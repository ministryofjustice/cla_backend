#!/bin/bash -e

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

cd /home/app
migrations
load_test_data

exec "$@"
