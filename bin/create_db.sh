#!/bin/bash -e

migrations() {
    python manage.py install_postgres_extensions
    python manage.py migrate --noinput

    python manage.py loaddata initial_groups.json
    python manage.py loaddata initial_category.json
    python manage.py loaddata initial_mattertype.json
    python manage.py loaddata initial_media_codes.json
    python manage.py loaddata initial_complaint_categories.json
    python manage.py loaddata initial_guidance_notes.json
}

load_seed_data() {
    if [ "$LOAD_SEED_DATA" == "True" ]; then

        python manage.py loaddata test_provider.json
        python manage.py loaddata test_provider_allocations.json
        python manage.py loaddata test_rotas.json
        python manage.py loaddata kb_from_knowledgebase.json

    fi
}

load_test_data() {
    if [ "$LOAD_TEST_DATA" == "True" ]; then
        python manage.py loaddata test_auth_clients.json
        python manage.py loaddata test_provider.json
        python manage.py loaddata test_provider_users.json
    fi
}

load_end_to_end_test_data() {
    if [ "$LOAD_END_TO_END_FIXTURES" == "True" ]; then

        python manage.py loaddata test_special_provider_case.json
        python manage.py loaddata test_callbacks.json
        python manage.py loaddata test_user_with_case.json
        python manage.py loaddata test_assign_f2f_case.json

    fi
}

admin_password() {
    if [ -n "$ADMIN_USER" ] && [ -n "$ADMIN_PASSWORD" ]; then
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('$ADMIN_USER', 'civil-legal-advice@digital.justice.gov.uk', '$ADMIN_PASSWORD')" | ./manage.py shell || echo "user already exists"
    fi
}

copy_old_client_data_to_new_table() {
    iif [ "$CLIENT_DATA_COPY" == "True" ]; then
        python manage.py copy_client_data_to_new_table
    fi
}

cd /home/app/

migrations
admin_password
load_seed_data
load_test_data
load_end_to_end_test_data
copy_old_client_data_to_new_table

exec "$@"
