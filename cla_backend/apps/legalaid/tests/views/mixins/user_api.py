from django.core.urlresolvers import reverse, NoReverseMatch

from rest_framework import status

from core.tests.test_base import CLAAuthBaseApiTestMixin


class UserAPIMixin(CLAAuthBaseApiTestMixin):
    def setUp(self):
        super(UserAPIMixin, self).setUp()

        self.other_users = self.get_other_users()

        self.detail_url = self.get_user_detail_url('me')

    def get_user_detail_url(self, user_pk):
        return reverse(
            '%s:user-detail' % self.API_URL_NAMESPACE, args=(),
            kwargs={'pk': user_pk}
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        self.assertRaises(NoReverseMatch, reverse, '%s:user-list' % self.API_URL_NAMESPACE)

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def assertUserEqual(self, data):
        raise NotImplementedError()

    def get_other_users(self):
        raise NotImplementedError()

    def test_get_me_allowed(self):
        response = self.client.get(
            self.detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertUserEqual(response.data)

    def test_get_different_user_not_allowed(self):
        detail_url = self.get_user_detail_url(self.other_users[0].pk)
        response = self.client.get(
            detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_methods_not_authorized(self):
        ### DETAIL
        self._test_post_not_authorized(self.detail_url, token=self.invalid_token)
        self._test_put_not_authorized(self.detail_url, token=self.invalid_token)
        self._test_delete_not_authorized(self.detail_url, token=self.invalid_token)
