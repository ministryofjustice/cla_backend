from django.core.urlresolvers import reverse, NoReverseMatch

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import CLAProviderAuthBaseApiTestMixin


class UserTests(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(UserTests, self).setUp()

        self.other_staff = make_recipe('cla_provider.staff', _quantity=3)

        self.detail_url = self.get_user_detail_url('me')

    def get_user_detail_url(self, user_pk):
        return reverse(
            'cla_provider:user-detail', args=(),
            kwargs={'pk': user_pk}
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        self.assertRaises(NoReverseMatch, reverse, 'cla_provider:user-list')

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_get_me_allowed(self):
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_data = dict(response.data)
        del resp_data['provider']['id']  # not sure why we are returning the provider id
        self.assertDictEqual(response.data, {
            'username': u'john',
            'first_name': u'',
            'last_name': u'',
            'email': u'lennon@thebeatles.com',
            'provider': {'name': u'Name1'},
            'is_manager': False
        })

    def test_get_different_user_not_allowed(self):
        detail_url = self.get_user_detail_url(self.other_staff[0].pk)
        response = self.client.get(detail_url,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_methods_not_authorized(self):
        ### DETAIL
        self._test_post_not_authorized(self.detail_url, self.operator_token)
        self._test_put_not_authorized(self.detail_url, self.operator_token)
        self._test_delete_not_authorized(self.detail_url, self.operator_token)
