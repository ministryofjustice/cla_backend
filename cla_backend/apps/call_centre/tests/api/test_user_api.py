from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string

from core.tests.mommy_utils import make_recipe
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from legalaid.tests.views.mixins.user_api import UserAPIMixin


class UserTestCase(CLAOperatorAuthBaseApiTestMixin, UserAPIMixin, APITestCase):
    def assertUserEqual(self, data):
        self.assertDictContainsSubset(
            {
                "username": u"john",
                "first_name": u"",
                "last_name": u"",
                "email": u"lennon@thebeatles.com",
                "is_manager": False,
                "is_cla_superuser": False,
            },
            data,
        )
        self.assertTrue("last_login" in data)
        self.assertTrue("created" in data)

    def get_other_users(self):
        return make_recipe("call_centre.operator", _quantity=3)

    def test_rest_password_other_user_as_manager(self):
        other_user = self.other_users[0].user
        reset_url = self.get_user_password_reset_url(other_user.username)
        response = self.client.post(
            reset_url,
            {"new_password": "b" * 10},
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def _assign_operators_to_organisation(self, foo_org, bar_org):

        operators = {"foo_org": [], "bar_org": [], "no_org": []}
        for index, operator in enumerate(self.other_users):
            if index % 2 == 0:
                operator.organisation = foo_org
                operators["foo_org"].append(operator.user.username)
            else:
                operator.organisation = bar_org
                operators["bar_org"].append(operator.user.username)
            operator.save()

        no_org_operators = make_recipe("call_centre.operator", _quantity=3)
        for operator in no_org_operators:
            operators["no_org"].append(operator.user.username)

        return operators

    def test_operator_manager_with_organisation_create_operator(self):
        foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")

        self.manager_token.user.operator.organisation = foo_org
        self.manager_token.user.operator.save()

        data = {
            "password": "foobarbaz1234567890",
            "username": get_random_string(),
            "first_name": "elton",
            "last_name": "john",
            "email": "example@example.com",
        }

        response = self.client.post(
            self.list_url, data, HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            self.get_user_detail_url(data["username"]),
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], data["username"])
        self.assertEqual(response.data["organisation"], foo_org.id)

    def test_operator_listing(self):
        foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")
        bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")
        operators = self._assign_operators_to_organisation(foo_org, bar_org)

        self.operator_manager.organisation = bar_org
        self.operator_manager.save()
        operators["bar_org"].append(self.operator_manager.user.username)

        self.operator.organisation = bar_org
        self.operator.save()
        operators["bar_org"].append(self.operator.user.username)

        url = reverse("%s:user-list" % self.API_URL_NAMESPACE)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token))

        for operator in response.data:
            self.assertNotIn(operator["username"], operators["foo_org"])
            self.assertIn(operator["username"], operators["bar_org"] + operators["no_org"])

    def test_cla_superuser_operator_listing(self):
        foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")
        bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")
        operators = self._assign_operators_to_organisation(foo_org, bar_org)
        # flatten dict of lists
        expected_usernames = list({x for v in operators.itervalues() for x in v})

        self.operator_manager.is_cla_superuser = True
        self.operator_manager.save()
        expected_usernames.append(self.operator_manager.user.username)
        expected_usernames.append(self.operator.user.username)

        url = reverse("%s:user-list" % self.API_URL_NAMESPACE)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token))

        actual_usernames = [operator["username"] for operator in response.data]
        self.assertItemsEqual(expected_usernames, actual_usernames)

    def test_cannot_reset_operator_password_of_another_organisation(self):
        foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")
        bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")

        self.manager_token.user.operator.organisation = foo_org
        self.manager_token.user.operator.save()

        other_user = self.other_users[0].user
        other_user.operator.organisation = bar_org
        other_user.operator.save()

        reset_url = self.get_user_password_reset_url(other_user.username)
        response = self.client.post(
            reset_url,
            {"new_password": "b" * 10},
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
