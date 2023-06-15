import json
import os

from django.db import connection
from django.utils import timezone

from legalaid.models import PersonalDetails


_dev_public_key = os.path.join(os.path.dirname(__file__), "keys", "diversity_dev_public.key")
_dev_private_key = os.path.join(os.path.dirname(__file__), "keys", "diversity_dev_private.key")


def _read_key_file(file_path):
    with open(file_path) as f:
        return f.read()


def _format_env_key(key):
    return key.replace("\\n", "\n")


def get_public_key():
    key = os.environ.get("DIVERSITY_PUBLIC_KEY")
    if key:
        return _format_env_key(key)
    return _read_key_file(os.environ.get("DIVERSITY_PUBLIC_KEY_PATH", _dev_public_key))


def get_private_key():
    key = os.environ.get("DIVERSITY_PRIVATE_KEY")
    if key:
        return _format_env_key(key)
    return _read_key_file(os.environ.get("DIVERSITY_PRIVATE_KEY_PATH", _dev_private_key))


def save_diversity_data(personal_details_pk, data):
    json_data = json.dumps(data)

    cursor = connection.cursor()
    sql = "UPDATE {table_name} SET diversity = pgp_pub_encrypt(%s, dearmor(%s)), diversity_modified = %s WHERE id = %s".format(
        table_name=PersonalDetails._meta.db_table
    )
    cursor.execute(sql, [json_data, get_public_key(), timezone.now(), personal_details_pk])


def load_diversity_data(personal_details_pk, passphrase, private_key_override=None):
    private_key = private_key_override or get_private_key()
    sql = "SELECT pgp_pub_decrypt(diversity, dearmor(%s), %s) FROM {table_name} WHERE id = %s".format(
        table_name=PersonalDetails._meta.db_table
    )

    cursor = connection.cursor()
    cursor.execute(sql, [private_key, passphrase, personal_details_pk])
    row = cursor.fetchone()[0]
    return json.loads(row)


def reencrypt(personal_details_pk, previous_private_key, previous_passphrase):
    previous_private_key = previous_private_key.replace("\\n", "\n")
    cursor = connection.cursor()
    sql = """UPDATE {table_name} SET diversity = pgp_pub_encrypt(
    pgp_pub_decrypt(diversity, dearmor(%s), %s),
    dearmor(%s))
    WHERE id = %s
    """.format(
        table_name=PersonalDetails._meta.db_table
    )
    cursor.execute(sql, [previous_private_key, previous_passphrase, get_public_key(), personal_details_pk])
