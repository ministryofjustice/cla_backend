from django.core.urlresolvers import reverse, NoReverseMatch

from rest_framework import status

from core.tests.test_base import CLAAuthBaseApiTestMixin

from cla_eventlog import event_registry


class EventAPIMixin(CLAAuthBaseApiTestMixin):
    def get_event_key(self):
        # getting the first event key in the registry as we don't know what's in there
        return event_registry._registry.keys()[0]

    def setUp(self):
        super(EventAPIMixin, self).setUp()

        self.detail_url = self.get_detail_url(self.get_event_key())

    def get_detail_url(self, action):
        return reverse(
            '%s:event-detail' % self.API_URL_NAMESPACE, args=(),
            kwargs={'action': action}
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        self.assertRaises(NoReverseMatch, reverse, '%s:event-list' % self.API_URL_NAMESPACE)

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_get_using_event_key(self):
        response = self.client.get(self.detail_url,
            HTTP_AUTHORIZATION='Bearer %s' % self.token, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        action = event_registry.get_event(self.get_event_key())

        # building expected response data
        codes = []
        for code, code_data in action.codes.items():
            codes.append({
                'code': code,
                'description': code_data['description']
            })
        self.assertItemsEqual(response.data, codes)

    def test_get_using_wrong_event_key_404(self):
        detail_url = self.get_detail_url('__wrong__')
        response = self.client.get(detail_url,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_methods_not_authorized(self):
        ### DETAIL
        self._test_post_not_authorized(self.detail_url, self.invalid_token)
        self._test_put_not_authorized(self.detail_url, self.invalid_token)
        self._test_delete_not_authorized(self.detail_url, self.invalid_token)
