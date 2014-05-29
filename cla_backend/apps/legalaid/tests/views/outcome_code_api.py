from django.core.urlresolvers import reverse

from rest_framework import status

from cla_common.constants import CASE_STATES, CASELOGTYPE_ACTION_KEYS

from core.tests.test_base import CLAAuthBaseApiTestMixin
from legalaid.constants import CASELOGTYPE_SUBTYPES

from ..base import generate_outcome_codes


class OutcomeCodeAPIMixin(CLAAuthBaseApiTestMixin):
    def setUp(self):
        super(OutcomeCodeAPIMixin, self).setUp()

        self.outcome_codes = generate_outcome_codes()

        self.list_url = reverse('%s:outcome_code-list' % self.API_URL_NAMESPACE)
        self.detail_url = reverse(
            '%s:outcome_code-detail' % self.API_URL_NAMESPACE, args=(),
            kwargs={'code': self.outcome_codes[0].code}
        )

    def test_get_without_filtering(self):
        """
        Ensure we can GET the list. By default, returns all outcome codes without
        filtering.
        """
        # LIST
        response = self.client.get(self.list_url,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual(
            [d['code'] for d in response.data],
            [outcome.code for outcome in self.outcome_codes if outcome.subtype == CASELOGTYPE_SUBTYPES.OUTCOME]
        )

        # DETAIL
        response = self.client.get(self.detail_url,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'CODE_OPEN')

    def test_get_with_case_state_filtering(self):
        """
        GET with case_state filtering.
        """
        # LIST
        response = self.client.get(self.list_url,
            { 'case_state': CASE_STATES.ACCEPTED },
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual(
            [d['code'] for d in response.data], ['CODE_ACCEPTED']
        )

        # DETAIL
        response = self.client.get(self.detail_url,
            { 'case_state': CASE_STATES.OPEN },
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'CODE_OPEN')

        # DETAIL not found (the outcomecode.case_state is OPEN but we're filtering by REJECTED)
        response = self.client.get(self.detail_url,
            { 'case_state': CASE_STATES.REJECTED },
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_with_action_key_filtering(self):
        """
        GET with action_key filtering.
        """
        # LIST
        action_key = CASELOGTYPE_ACTION_KEYS.DECLINE_SPECIALISTS
        response = self.client.get(self.list_url,
            { 'action_key': action_key },
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual(
            [d['code'] for d in response.data],
            [outcome.code for outcome in self.outcome_codes if outcome.action_key == action_key]
        )

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        ### LIST
        self._test_post_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_methods_not_authorized(self):
        ### LIST
        self._test_get_not_authorized(self.list_url, self.invalid_token)
        self._test_post_not_authorized(self.list_url, self.invalid_token)
        self._test_put_not_authorized(self.list_url, self.invalid_token)
        self._test_delete_not_authorized(self.list_url, self.invalid_token)

        ### DETAIL
        self._test_get_not_authorized(self.detail_url, self.invalid_token)
        self._test_post_not_authorized(self.detail_url, self.invalid_token)
        self._test_put_not_authorized(self.detail_url, self.invalid_token)
        self._test_delete_not_authorized(self.detail_url, self.invalid_token)
