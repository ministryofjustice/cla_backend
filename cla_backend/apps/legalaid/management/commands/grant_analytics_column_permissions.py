from django.core.management import BaseCommand
from django.db import connection
from psycopg2.extensions import AsIs  # AsIs is used to pass in strings to the SQL statement without a quotation mark.
from django.apps import apps
import os
import logging

logger = logging.getLogger()

PG_USER_NAME = "analytics"
PG_USER_PASSWORD = os.environ.get("ANALYTICS_DB_PASSWORD")


def get_all_non_restricted_models(models):
    """ Gets all non-restricted fields and the model they belong to.

    Args:
        List[django.Model]: List of models to check through

    Return:
        List[List[db_table_name, db_column_name]]
    """
    non_restricted_models = {}
    for model in models:
        non_restricted_columns = get_all_non_restricted_columns(model)
        if len(non_restricted_columns) != 0:
            non_restricted_models[model._meta.db_table] = non_restricted_columns

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
            non_restricted_columns.append(column.name)

    return non_restricted_columns


def does_pg_user_exist(username):
    with connection.cursor() as cursor:
        cursor.execute("select * from pg_catalog.pg_roles where rolname=%s", [username])
        roles = cursor.fetchall()
        return len(roles) != 0


def create_pg_user(username, password):
    if password is None or password == "":
        raise ValueError("ANALYTICS_DB_PASSWORD must be set.")
    with connection.cursor() as cursor:
        cursor.execute("CREATE ROLE %s WITH LOGIN PASSWORD %s", [AsIs(username), password])
        cursor.execute("GRANT CONNECT ON DATABASE cla_backend TO %s", [AsIs(username)])
    logger.info("Created pg user: {username}".format(username=username))


def does_view_exist(view_name):
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from pg_catalog.pg_views pv where schemaname='public' and viewname='{view_name}'".format(
                view_name=view_name
            )
        )
        views = cursor.fetchall()
        return len(views) != 0


def delete_view(view_name):
    with connection.cursor() as cursor:
        cursor.execute("DROP VIEW {view_name}".format(view_name=view_name))
    logger.info("Dropped view {view_name}".format(view_name=view_name))


class Command(BaseCommand):
    help = "Grants the analytics postgres user permissions read permissions for columns not containing sensitive personal data as defined by the Analytics model class."

    def handle(self, *args, **options):

        if not does_pg_user_exist(PG_USER_NAME):
            create_pg_user(PG_USER_NAME, PG_USER_PASSWORD)

        # Gets a dict of table names with a list of non-sensitive columns
        non_sensitive_models = get_all_non_restricted_models(apps.get_models())

        sql_commands = []

        for model, columns in non_sensitive_models.iteritems():
            view_name = "{model_name}_view".format(model_name=model)
            if does_view_exist(view_name):
                delete_view(view_name)

            formatted_columns = []
            for column in columns:
                formatted_columns.append("{model_name}.{column}".format(model_name=model, column=column))
            formatted_columns = ", ".join(formatted_columns)

            sql_commands.append(
                "CREATE VIEW {view_name} AS SELECT {columns} FROM {table}".format(
                    view_name=view_name, columns=formatted_columns, table=model
                )
            )
            sql_commands.append("GRANT SELECT ON {view_name} TO {user}".format(view_name=view_name, user=PG_USER_NAME))

        with connection.cursor() as cursor:
            for command in sql_commands:
                cursor.execute(command)
                logger.info("Executed: {command}".format(command=command))
