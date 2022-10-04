from io import StringIO
from collections import OrderedDict

from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
from django.db.transaction import atomic
from django.test import TestCase

from oauth2_provider.models import Application


class ClientDataCopyCommandTest(TestCase):

    OLD_CLIENT_DATA = OrderedDict([
        ("client_id", "test"),
        ("redirect_uri", "http://localhost:1234"),
        ("client_type", "test_type"),
        ("client_secret", "test_secret"),
        ("name", "test_name"),
        ("user_id", 1234)])

    def setUp(self):
        super(ClientDataCopyCommandTest, self).setUp()
        self.test_user = User.objects.create(
            id=self.OLD_CLIENT_DATA["user_id"],
            username="test",
            password="test",
            email="test@test.com")
        self.create_client_data()

    def run_management_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "copy_client_data_to_new_table",
            *args,
            stdout=out,
            stderr=StringIO())
        return out.getvalue()

    def assert_application_data_is_correct(self, application_model):
        assert application_model.user == self.test_user
        assert application_model.name == self.OLD_CLIENT_DATA["name"]
        assert application_model.client_type == self.OLD_CLIENT_DATA["client_type"]
        assert application_model.client_id == self.OLD_CLIENT_DATA["client_id"]
        assert application_model.client_secret == self.OLD_CLIENT_DATA["client_secret"]
        assert application_model.redirect_uris == self.OLD_CLIENT_DATA["redirect_uri"]
        assert application_model.authorization_grant_type == "password"

    def create_client_data(self):
        create_client_data_query = "CREATE TABLE oauth2_client (client_id varchar(255), redirect_uri varchar(255), " \
            "client_type varchar(255), client_secret varchar(255), name varchar(255), user_id varchar(255))"
        with connection.cursor() as cursor:
            cursor.execute(create_client_data_query)
            cursor.execute(
                "INSERT INTO oauth2_client VALUES ('{}', '{}', '{}', '{}', '{}', {})".format(*self.OLD_CLIENT_DATA.values()))

    def test_data_copy_handles_already_existing_data(self):

        Application.objects.all().delete()

        Application.objects.create(
            user=self.test_user,
            name=self.OLD_CLIENT_DATA["name"],
            client_type=self.OLD_CLIENT_DATA["client_type"],
            client_id=self.OLD_CLIENT_DATA["client_id"],
            client_secret=self.OLD_CLIENT_DATA["client_secret"],
            redirect_uris=self.OLD_CLIENT_DATA["redirect_uri"],
            authorization_grant_type="password",
        )
        with atomic():
            self.run_management_command()

        final_applications = Application.objects.all()
        assert final_applications.count() == 1
        self.assert_application_data_is_correct(final_applications[0])

    def test_data_copy_success(self):
        Application.objects.all().delete()

        self.run_management_command()

        final_applications = Application.objects.all()
        assert final_applications.count() == 1
        self.assert_application_data_is_correct(final_applications[0])
