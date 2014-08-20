from django.core.urlresolvers import reverse, NoReverseMatch

from rest_framework import status

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import CLAAuthBaseApiTestMixin

from cla_eventlog.constants import LOG_LEVELS
from cla_eventlog.models import Log
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
        self._test_post_not_authorized(self.detail_url, token=self.invalid_token)
        self._test_put_not_authorized(self.detail_url, token=self.invalid_token)
        self._test_delete_not_authorized(self.detail_url, token=self.invalid_token)


class ImplicitEventCodeViewTestCaseMixin(object):
    """
    This is for endpoints which mainly create implicit outcome after
    an action (e.g. close case, accept case etc.).

    The user is not given the possibility to specify an outcome code.
    """
    NO_BODY_RESPONSE = True

    def setUp(self):
        super(ImplicitEventCodeViewTestCaseMixin, self).setUp()
        self.url = self.get_url()

    def get_url(self, reference=None):
        raise NotImplementedError()

    def test_methods_not_allowed(self):
        self._test_get_not_allowed(self.url)
        self._test_patch_not_allowed(self.url)
        self._test_delete_not_allowed(self.url)

    def test_invalid_reference(self):
        url = self.get_url(reference='invalid')

        response = self.client.post(url, data={},
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_401_if_not_logged_in(self):
        response = self.client.post(self.url, data={})
        self.assertTrue(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def get_default_post_data(self):
        return {
            'notes': 'lorem ipsum'
        }

    def test_successful(self):
        # before, no logs
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_default_post_data()
        response = self.client.post(
            self.url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        if self.NO_BODY_RESPONSE:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # after, log entry created
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]

        self.assertEqual(log.case, self.check)
        self.assertEqual(log.notes, data['notes'])
        self.assertEqual(log.created_by, self.user)


class ExplicitEventCodeViewTestCaseMixin(ImplicitEventCodeViewTestCaseMixin):
    """
    This is for endpoints which create explicit outcomes after
    an action (e.g. reject case etc.).

    The user is given the possibility to specify an outcome code from a list of
    valid ones.
    """
    def get_event_code(self):
        """
        Should return a __valid__ code for this endpoints.
        """
        raise NotImplementedError()

    def get_default_post_data(self):
        data = super(ExplicitEventCodeViewTestCaseMixin, self).get_default_post_data()
        data['event_code'] = self.get_event_code()
        return data


class LogAPIMixin(CLAAuthBaseApiTestMixin):
    def setUp(self):
        super(LogAPIMixin, self).setUp()
        self.case_obj = make_recipe('legalaid.case')
        self.high_logs = make_recipe(
            'cla_eventlog.log', case=self.case_obj, level=LOG_LEVELS.HIGH,
            code="HIGH_", _quantity=4
        )
        self.minor_logs = make_recipe(
            'cla_eventlog.log', case=self.case_obj, level=LOG_LEVELS.MINOR,
            code="MINIOR_", _quantity=4
        )

        self.list_url = self.get_list_url(self.case_obj.reference)

    def get_list_url(self, case_ref):
        return reverse(
            '%s:log-list' % self.API_URL_NAMESPACE, args=(),
            kwargs={'case_reference': case_ref}
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        self._test_post_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

    def test_methods_not_authorized(self):
        self._test_get_not_authorized(self.list_url, self.invalid_token)

    def test_get(self):
        response = self.client.get(
            self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual(
            [log.code for log in self.high_logs],
            [log['code'] for log in response.data]
        )
