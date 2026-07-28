import textwrap
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Installs pgcrypto if it is missing.
    Currently called from migrations.startup init script inside the docker container.
    """

    help = textwrap.dedent(__doc__).strip()

    def handle(self, *args, **options):
        from django.db import connections, DEFAULT_DB_ALIAS

        connection = connections[DEFAULT_DB_ALIAS]
        if connection.vendor != "postgresql":
            print("Current database is not postgres, not installing extensions")
            return
        cursor = connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS tablefunc")
