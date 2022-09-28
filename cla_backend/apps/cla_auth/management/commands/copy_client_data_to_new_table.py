import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connections, connection
from django.db.transaction import atomic
from django.db.utils import ConnectionDoesNotExist, IntegrityError

from oauth2_provider.models import Application

from . import sql


class Command(BaseCommand):
    help = (
        "Copies client data used by older provider.oauth2 package tables"
        "to newer tables used by oauth2_provider tables"
    )

    def handle(self, *args, **options):
        clients = self.get_queryset()
        try:
            for client in clients:
                user = None

                if client["user_id"] is not None:
                    user = User.objects.get(pk=client["user_id"])

                Application.objects.create(
                    user=user,
                    name=client["name"],
                    client_type=client["client_type"],
                    client_id=client["client_id"],
                    client_secret=client["client_secret"],
                    redirect_uris=client["redirect_uris"],
                    authorization_grant_type="password",
                )
        except IntegrityError as e:
            # I am passing this error, it means the details are in the table already.
            # as a precaution this script doesnt get taken out immediatly I don't 
            # want it failing the start up script for backend.
            pass

    def get_cursor(self):
        try:
            return connections["default"].cursor()
        except ConnectionDoesNotExist:
            return connection.cursor()

    def get_queryset(self):
        path = os.path.join(sql.__path__[0], "get_old_client_data.sql")
        with open(path, "r") as f:
            query = f.read()
        return self.execute_query(query)

    def execute_query(self, query):
        """
        Returns the result as a list of dicts
        """
        with atomic():
            cursor = self.get_cursor()
            try:
                cursor.execute(query)
                fieldnames = [name[0] for name in cursor.description]
                result = []
                for row in cursor.fetchall():
                    rowset = []
                    for field in zip(fieldnames, row):
                        rowset.append(field)
                    result.append(dict(rowset))
                return result
            finally:
                cursor.close()
