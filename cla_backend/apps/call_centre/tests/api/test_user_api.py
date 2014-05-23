from django.core.urlresolvers import reverse, NoReverseMatch

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin


class UserTests(CLAOperatorAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(UserTests, self).setUp()

        self.other_operators = make_recipe('call_centre.operator', _quantity=3)

        self.detail_url = self.get_user_detail_url('me')

    def get_user_detail_url(self, user_pk):
        return reverse(
            'call_centre:user-detail', args=(),
            kwargs={'pk': user_pk}
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        self.assertRaises(NoReverseMatch, reverse, 'call_centre:user-list')

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_get_me_allowed(self):
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, {
            'username': u'john',
            'first_name': u'',
            'last_name': u'',
            'email': u'lennon@thebeatles.com',
            'is_operator_superuser': False
        })

    def test_get_different_user_not_allowed(self):
        detail_url = self.get_user_detail_url(self.other_operators[0].pk)
        response = self.client.get(detail_url,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_methods_not_authorized(self):
        ### DETAIL
        self._test_post_not_authorized(self.detail_url, self.staff_token)
        self._test_put_not_authorized(self.detail_url, self.staff_token)
        self._test_delete_not_authorized(self.detail_url, self.staff_token)
