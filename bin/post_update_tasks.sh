#!/bin/bash -e

copy_old_client_data_to_new_table() {
    if [ "$MIGRATE_OAUTH_DATA" == "True" ]; then
        python manage.py copy_client_data_to_new_table
    fi
}

cd /home/app/

copy_old_client_data_to_new_table

exec "$@"
