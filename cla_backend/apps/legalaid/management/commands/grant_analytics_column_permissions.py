from django.core.management import BaseCommand
from django.db import connection
from psycopg2.extensions import AsIs  # AsIs is used to pass in strings to the SQL statement without a quotation mark.
from django.apps import apps
import os
import logging

logger = logging.getLogger()

PG_USER_NAME = "Analytics"
PG_USER_PASSWORD = os.environ.get("ANALYTICS_DB_PASSWORD")


def get_all_non_restricted_models(models):
    """ Gets all non-restricted fields and the model they belong to.

    Args:
        List[django.Model]: List of models to check through

    Return:
        List[List[db_table_name, db_column_name]]
    """
    non_restricted_models = []
    for model in models:
        non_restricted_columns = get_all_non_restricted_columns(model)
        for column in non_restricted_columns:
            non_restricted_models.append([model._meta.db_table, column.name])

    return non_restricted_models


def get_all_non_restricted_columns(model):
    """ Gets all non restricted columns from the relevant django model.
    Columns are non-restricted if the model has Analytics._allow_analytics set to True and the columns are not listed in Analytics._PII.

    Args:
        model (django.Model): A django model

    Return:
        List[django.model.field]
    """
    if not hasattr(model, "Analytics"):
        return []

    if not hasattr(model.Analytics, "_allow_analytics") or not model.Analytics._allow_analytics:
        return []

    non_restricted_columns = []
    pii_columns = []

    # If column contains sensitive information it should be restricted.
    if hasattr(model.Analytics, "_PII"):
        pii_columns = model.Analytics._PII

    for column in model._meta.get_fields():
        if column not in pii_columns and not column.is_relation:
            non_restricted_columns.append(column)

    return non_restricted_columns


def does_pg_user_exist(username):
    with connection.cursor() as cursor:
        cursor.execute("select * from pg_catalog.pg_roles where rolname=%s", [username])
        roles = cursor.fetchall()
        return len(roles) != 0


def create_pg_user(username, password):
    with connection.cursor() as cursor:
        cursor.execute("CREATE ROLE %s WITH LOGIN PASSWORD %s", [AsIs(username), password])
        cursor.execute("GRANT CONNECT ON DATABASE cla_backend TO %s", [AsIs(username)])
    logger.info("Created pg user: {username}".format(username=username))


class Command(BaseCommand):
    help = "Grants the analytics postgres user permissions read permissions for columns not containing sensitive personal data as defined by the Analytics model class."

    def handle(self, *args, **options):
        if not does_pg_user_exist(PG_USER_NAME):
            create_pg_user(PG_USER_NAME, PG_USER_PASSWORD)

        sql_commands = [
            'GRANT SELECT("{column}") ON {table} TO {username}'.format(
                column=column, table=table, username=PG_USER_NAME
            )
            for inner_list in get_all_non_restricted_models(apps.get_models())
            for table, column in [inner_list]
        ]

        with connection.cursor() as cursor:
            for command in sql_commands:
                cursor.execute(command)
                logger.info("Executed: {command}".format(command=command))
