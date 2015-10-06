import textwrap
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    """
    Installs pgcrypto if it is missing.
    Currently called from migrations.startup init script inside the docker container.
    """
    help = textwrap.dedent(__doc__).strip()

    def handle_noargs(self, **options):
        from django.db import connections, DEFAULT_DB_ALIAS

        connection = connections[DEFAULT_DB_ALIAS]
        if connection.vendor != 'postgresql':
            print 'Current database is not postgres, not installing extensions'
            return
        cursor = connection.cursor()
        cursor.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')
