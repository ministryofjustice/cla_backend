import os
import sys

from django.core.management.base import BaseCommand
from django.db import connections, connection
from django.db.transaction import atomic
from django.db.utils import ConnectionDoesNotExist

from . import sql


def get_cursor():
    try:
        return connections["default"].cursor()
    except ConnectionDoesNotExist:
        return connection.cursor()

class Command(BaseCommand):
    help = (
        "Copies client data used by older provider.oauth2 package tables"
        "to newer tables used by oauth2_provider tables"
    )

    def handle(self, *args, **options):
        self.get_queryset()

    def get_queryset(self):
        path = os.path.join(sql.__path__[0], "get_old_client_data.sql")
        with open(path, "r") as f:
            query = f.read()
        return self.execute_query(query)

    def execute_query(self, query):
        with atomic():
            cursor = get_cursor()
            try:
                cursor.execute(query)
                self.description = cursor.description
                return cursor.fetchall()
            finally:
                cursor.close()
