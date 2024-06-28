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

    non_restricted_columns = ["id"]  # If we are allowing analytics then the ID should always be included.
    pii_columns = []

    # If column contains sensitive information it should be restricted.
    if hasattr(model.Analytics, "_PII"):
        pii_columns = model.Analytics._PII

    for column in model._meta.get_fields():
        if column.name in pii_columns:
            continue
        # If the column is auto generated or an inverse m2m relation, it will not exist as a column in the database.
        # Django created a fake field representing this relationship.
        if column.auto_created or hasattr(column, "m2m_reverse_field_name"):
            continue
        if column.column:
            non_restricted_columns.append(column.column)

    return non_restricted_columns


def does_pg_user_exist(username):
    """Checks if a given postgres role exists

    Args:
        username (str): User role

    Returns:
        Bool: Does the role exist
    """
    with connection.cursor() as cursor:
        cursor.execute("select * from pg_catalog.pg_roles where rolname=%s", [username])
        roles = cursor.fetchall()
        return len(roles) != 0


def create_pg_user(username, password):
    """Creates a postgres user, giving them permissions to connect to the database and usage of the public schema.
    This does not give any permissions for tables within the schema.

    Args:
        username (str): Postgres user name
        password (str): User password

    Raises:
        ValueError: ValueError will be raised if a password is not given.
    """
    if password is None or password == "":
        raise ValueError("ANALYTICS_DB_PASSWORD must be set.")
    with connection.cursor() as cursor:
        cursor.execute("CREATE ROLE %s WITH LOGIN PASSWORD %s", [AsIs(username), password])
        cursor.execute("GRANT CONNECT ON DATABASE cla_backend TO %s", [AsIs(username)])
        cursor.execute("GRANT USAGE ON SCHEMA public TO %s", [AsIs(username)])
    logger.info("Created pg user: {username}".format(username=username))


def does_view_exist(view_name):
    """Checks if a given view exists in the public schema

    Args:
        view_name (str): View name

    Returns:
        Bool: Does view exist
    """
    command = "select * from pg_catalog.pg_views pv where schemaname='public' and viewname='{view_name}'".format(
        view_name=view_name
    )
    with connection.cursor() as cursor:
        cursor.execute(command)
        views = cursor.fetchall()
        return len(views) != 0


def create_view(view_name, table, columns):
    """Creates a view with the given name in the public schema.

    Args:
        view_name (str): Name of the view
        table (str): Name of the table the columns belong to
        columns (list[str]): List of column names to include in the view
    """
    command = "CREATE VIEW %s AS SELECT %s FROM %s"
    if "diagnosis_diagnosistraversal.nodes" in columns:
        columns = columns.replace("diagnosis_diagnosistraversal.nodes", "json_array_elements(nodes) as nodes")
    with connection.cursor() as cursor:
        cursor.execute(command, [AsIs(view_name), AsIs(columns), AsIs(table)])
        logger.info("Created view: {view_name} with columns: {columns}".format(view_name=view_name, columns=columns))


def grant_permission_for_view(view_name, role):
    """Grants the role permission to select from the given view.

    Args:
        view_name (str): Name of the view
        role (str): Postgres role name
    """
    command = "GRANT SELECT ON %s TO %s"
    with connection.cursor() as cursor:
        cursor.execute(command, [AsIs(view_name), AsIs(role)])
        logger.info("Granted {role} view permissions on view: {view_name}".format(role=role, view_name=view_name))


def delete_view(view_name):
    command = "DROP VIEW %s"
    with connection.cursor() as cursor:
        cursor.execute(command, [AsIs(view_name)])
    logger.info("Dropped view {view_name}".format(view_name=view_name))


class Command(BaseCommand):
    help = "Creates restricted views containing only non personal data, as defined by the Analytics model class. Then grants the analytics user read permission on these views, if the analytics user does not exist it will be created."

    def handle(self, *args, **options):

        if not does_pg_user_exist(PG_USER_NAME):
            create_pg_user(PG_USER_NAME, PG_USER_PASSWORD)

        # Gets a dict of table names with a list of non-sensitive columns
        non_sensitive_models = get_all_non_restricted_models(apps.get_models())

        for model, columns in non_sensitive_models.iteritems():
            view_name = "{model_name}_view".format(model_name=model)
            if does_view_exist(view_name):
                delete_view(view_name)

            formatted_columns = []
            for column in columns:
                formatted_columns.append("{model_name}.{column}".format(model_name=model, column=column))
            formatted_columns = ", ".join(formatted_columns)

            create_view(view_name, model, formatted_columns)
            grant_permission_for_view(view_name, PG_USER_NAME)
