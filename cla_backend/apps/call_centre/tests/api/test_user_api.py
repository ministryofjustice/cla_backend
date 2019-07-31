from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse

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
            operator.save()
            operators["no_org"].append(operator.user.username)

        return operators

    def test_operator_listing(self):
        foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")
        foo_org.save()
        bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")
        bar_org.save()
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
        foo_org.save()
        bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")
        bar_org.save()
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
