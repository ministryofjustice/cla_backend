# coding=utf-8
from __future__ import unicode_literals

from django.db import connection, migrations


def add_trigram_indexes(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION pg_trgm;")
        cursor.execute(
            "CREATE INDEX case_reference_trgm_idx ON " "legalaid_case USING gist (UPPER(reference) gist_trgm_ops);"
        )
        cursor.execute(
            "CREATE INDEX case_search_field_trgm_idx ON "
            "legalaid_case USING gist (UPPER(search_field) gist_trgm_ops);"
        )
        cursor.execute(
            "CREATE INDEX case_laa_reference_trgm_idx ON "
            "legalaid_case USING gist (UPPER(text(laa_reference)) gist_trgm_ops);"
        )
        cursor.execute(
            "CREATE INDEX personaldetails_full_name_trgm_idx ON "
            "legalaid_personaldetails USING gist (UPPER(full_name) gist_trgm_ops);"
        )
        cursor.execute(
            "CREATE INDEX personaldetails_street_trgm_idx ON "
            "legalaid_personaldetails USING gist (UPPER(street) gist_trgm_ops);"
        )
        cursor.execute(
            "CREATE INDEX personaldetails_postcode_trgm_idx ON "
            "legalaid_personaldetails USING gist (UPPER(postcode) gist_trgm_ops);"
        )
        cursor.execute(
            "CREATE INDEX personaldetails_search_field_trgm_idx ON "
            "legalaid_personaldetails USING gist (UPPER(search_field) gist_trgm_ops);"
        )


def remove_trigram_indexes(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("DROP INDEX case_reference_trgm_idx;")
        cursor.execute("DROP INDEX case_search_field_trgm_idx;")
        cursor.execute("DROP INDEX case_laa_reference_trgm_idx;")
        cursor.execute("DROP INDEX personaldetails_full_name_trgm_idx;")
        cursor.execute("DROP INDEX personaldetails_street_trgm_idx;")
        cursor.execute("DROP INDEX personaldetails_postcode_trgm_idx;")
        cursor.execute("DROP INDEX personaldetails_search_field_trgm_idx;")
        cursor.execute("DROP EXTENSION pg_trgm;")


class Migration(migrations.Migration):

    dependencies = [("legalaid", "0017_case_is_urgent")]

    operations = [migrations.RunPython(add_trigram_indexes, remove_trigram_indexes)]
