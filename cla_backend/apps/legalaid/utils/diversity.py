import json

from django.conf import settings
from django.db import connection
from django.utils import timezone

from legalaid.models import PersonalDetails


def get_public_key():
    with open(settings.DIVERSITY_PUBLIC_KEY_PATH, 'r') as afile:
        key = afile.read()
    return key


def get_private_key():
    with open(settings.DIVERSITY_PRIVATE_KEY_PATH, 'r') as afile:
        key = afile.read()
    return key


def save_diversity_data(personal_details_pk, data):
    json_data = json.dumps(data)

    cursor = connection.cursor()
    sql = "UPDATE {table_name} SET diversity = pgp_pub_encrypt(%s, dearmor(%s)), diversity_modified = %s WHERE id = %s".format(
        table_name=PersonalDetails._meta.db_table
    )
    cursor.execute(sql, [
        json_data, get_public_key(),
        timezone.now(), personal_details_pk
    ])


def load_diversity_data(personal_details_pk, passphrase):
    sql = "SELECT pgp_pub_decrypt(diversity, dearmor(%s), %s) FROM {table_name} WHERE id = %s".format(
        table_name=PersonalDetails._meta.db_table
    )

    cursor = connection.cursor()
    cursor.execute(sql, [
        get_private_key(), passphrase, personal_details_pk
    ])
    row = cursor.fetchone()[0]
    return json.loads(row)
