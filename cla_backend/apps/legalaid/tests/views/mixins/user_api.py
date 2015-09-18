from django.core.urlresolvers import reverse
from rest_framework import status

from cla_auth.models import AccessAttempt


class UserAPIMixin(object):
    def setUp(self):
        super(UserAPIMixin, self).setUp()

        self.other_users = self.get_other_users()

        self.detail_url = self.get_user_detail_url('me')

        self.list_url = reverse('%s:user-list' % self.API_URL_NAMESPACE)

    def get_user_password_reset_url(self, username):
        return reverse('%s:user-password-reset' % self.API_URL_NAMESPACE, args=(),
                       kwargs={'user__username': username})

    def get_user_reset_lockout_url(self, username):
        return reverse(
            '%s:user-reset-lockout' % self.API_URL_NAMESPACE,
            args=(),
            kwargs={'user__username': username}
        )

    def get_user_detail_url(self, username):
        return reverse(
            '%s:user-detail' % self.API_URL_NAMESPACE, args=(),
            kwargs={'user__username': username}
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # LIST
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        # DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def assertUserEqual(self, data):
        raise NotImplementedError()

    def get_other_users(self):
        raise NotImplementedError()

    def test_methods_not_authorized(self):
        # LIST
        self._test_post_not_authorized(self.list_url, token=self.invalid_token)
        self._test_get_not_authorized(self.list_url, token=self.invalid_token)

        self._test_put_not_authorized(self.list_url, token=self.invalid_token)
        self._test_delete_not_authorized(self.list_url, token=self.invalid_token)

        # DETAIL
        self._test_post_not_authorized(self.detail_url, token=self.invalid_token)
        self._test_put_not_authorized(self.detail_url, token=self.invalid_token)
        self._test_delete_not_authorized(self.detail_url, token=self.invalid_token)

        self._test_post_not_authorized(self.list_url, token=self.token)
        self._test_get_not_authorized(self.list_url, token=self.token)

    # get/me - get/<user>

    def test_get_me_allowed(self):
        response = self.client.get(
            self.detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertUserEqual(response.data)

    def test_get_different_user_not_allowed(self):
        detail_url = self.get_user_detail_url(self.other_users[0].user.username)
        response = self.client.get(
            detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, self.OTHER_USER_ACCESS_STATUS_CODE)

    def test_get_different_user_of_own_organisation_allowed_as_manager(self):
        other_user = self.other_users[1]
        other_user.provider = self.provider
        other_user.save()

        detail_url = self.get_user_detail_url(other_user.user.username)
        response = self.client.get(
            detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(self.provider, other_user.provider)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # list

    def test_manager_can_list_organisation_users(self):
        response = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    # create

    def test_manager_can_create_organisation_users(self):
        response = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        initial_user_count = len(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            'password': 'foobarbaz1234567890',
            'username': 'cooldude',
            'first_name': 'elton',
            'last_name': 'john',
            'email': 'example@example.com'

        }

        response2 = self.client.post(
            self.list_url,
            data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        response3 = self.client.get(
            self.list_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )

        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(initial_user_count+1, len(response3.data))

    def test_password_length_validation_on_create(self):

        data = {
            'password': 'pw',
            'username': 'cooldude',
            'first_name': 'elton',
            'last_name': 'john',
            'email': 'example@example.com'

        }

        response = self.client.post(
            self.list_url,
            data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response)
        self.assertEqual(response.data['password'], [u"Password must be at least 10 characters long."])

    def test_duplicate_username_validation(self):
        data = {
            'password': 'pw'*10,
            'username': 'cooldude',
            'first_name': 'elton',
            'last_name': 'john',
            'email': 'example@example.com'

        }

        response = self.client.post(
            self.list_url,
            data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response)

        response2 = self.client.post(
            self.list_url,
            data,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )
        self.assertEqual(response2.data['non_field_errors'], ["An account with this username already exists."])

    # reset password

    def test_reset_password_me(self):
        reset_url = self.get_user_password_reset_url('me')
        me = self.token.user
        me.set_password('a'*10)
        me.save()
        response = self.client.post(
            reset_url,
            {
                'old_password': 'a'*10,
                'new_password': 'b'*10
            },
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reset_password_me_correct_old_password(self):
        reset_url = self.get_user_password_reset_url('me')
        me = self.token.user
        me.set_password('a'*10)
        me.save()
        response = self.client.post(
            reset_url,
            {
                'old_password': 'a'*10,
                'new_password': 'b'*10
            },
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reset_password_me_wrong_old_password_not_allowed(self):
        reset_url = self.get_user_password_reset_url('me')
        me = self.token.user
        me.set_password('a'*10)
        me.save()
        response = self.client.post(
            reset_url,
            {
                'old_password': 'z'*10,
                'new_password': 'b'*10
            },
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # reset lockout

    def test_reset_lockout_not_allowed_if_not_manager(self):
        other_user = self.other_users[1]
        other_user.provider = self.provider
        other_user.save()

        other_username = other_user.user.username

        reset_lockout = self.get_user_reset_lockout_url(other_username)
        response = self.client.post(
            reset_lockout,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.token)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reset_lockout_if_manager(self):
        other_user = self.other_users[1]
        other_user.provider = self.provider
        other_user.save()

        other_username = other_user.user.username

        # creating AccessAttempts

        AccessAttempt.objects.create_for_username('different_username')
        for index in range(5):
            AccessAttempt.objects.create_for_username(other_username)

        self.assertEqual(
            AccessAttempt.objects.filter(username=other_username).count(), 5
        )

        # make request
        reset_lockout = self.get_user_reset_lockout_url(other_username)
        response = self.client.post(
            reset_lockout,
            HTTP_AUTHORIZATION=self.get_http_authorization(token=self.manager_token)
        )

        # asserts
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            AccessAttempt.objects.filter(username=other_username).count(), 0
        )
