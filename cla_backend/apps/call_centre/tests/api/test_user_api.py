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

    def test_operator_listing(self):
        organisation_foo = make_recipe("call_centre.organisation", name="Organisation Foo")
        organisation_foo.save()
        organisation_bar = make_recipe("call_centre.organisation", name="Organisation Bar")
        organisation_bar.save()

        foo_operators = []
        bar_operators = []
        for index, operator in enumerate(self.other_users):
            if index % 2 == 0:
                operator.organisation = organisation_foo
                foo_operators.append(operator.user.username)
            else:
                operator.organisation = organisation_bar
                bar_operators.append(operator.user.username)
            operator.save()

        self.operator_manager.organisation = organisation_bar
        self.operator_manager.save()
        bar_operators.append(self.operator_manager.user.username)

        self.operator.organisation = organisation_bar
        self.operator.save()
        bar_operators.append(self.operator.user.username)

        operators = make_recipe("call_centre.operator", _quantity=3)
        operators_without_organisation = []
        for operator in operators:
            operator.save()
            operators_without_organisation.append(operator.user.username)

        url = reverse("%s:user-list" % self.API_URL_NAMESPACE)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token))

        for operator in response.data:
            self.assertNotIn(operator["username"], foo_operators)
            self.assertIn(operator["username"], bar_operators + operators_without_organisation)
