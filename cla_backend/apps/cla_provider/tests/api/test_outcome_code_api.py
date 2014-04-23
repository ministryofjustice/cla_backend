from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_REJECTED, \
    CASE_STATE_ACCEPTED

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin, make_recipe


class OutcomeCodesTests(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(OutcomeCodesTests, self).setUp()

        self.outcome_codes = [
            make_recipe('legalaid.tests.outcome_code', code="CODE_OPEN", case_state=CASE_STATE_OPEN),
            make_recipe('legalaid.tests.outcome_code', code="CODE_ACCEPTED", case_state=CASE_STATE_ACCEPTED),
            make_recipe('legalaid.tests.outcome_code', code="CODE_REJECTED", case_state=CASE_STATE_REJECTED),
        ]

        self.list_url = reverse('cla_provider:outcomecode-list')
        self.detail_url = reverse(
            'cla_provider:outcomecode-detail', args=(),
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
            ['CODE_OPEN', 'CODE_REJECTED', 'CODE_ACCEPTED']
        )

        # DETAIL
        response = self.client.get(self.detail_url,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'CODE_OPEN')

    def test_get_with_filtering(self):
        """
        GET with case_state filtering.
        """
        # LIST
        response = self.client.get(self.list_url,
            { 'case_state': CASE_STATE_ACCEPTED },
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual(
            [d['code'] for d in response.data], ['CODE_ACCEPTED']
        )

        # DETAIL
        response = self.client.get(self.detail_url,
            { 'case_state': CASE_STATE_OPEN },
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'CODE_OPEN')

        # DETAIL not found (the outcomecode.case_state is OPEN but we're filtering by REJECTED)
        response = self.client.get(self.detail_url,
            { 'case_state': CASE_STATE_REJECTED },
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        self._test_get_not_authorized(self.list_url, self.operator_token)
        self._test_post_not_authorized(self.list_url, self.operator_token)
        self._test_put_not_authorized(self.list_url, self.operator_token)
        self._test_delete_not_authorized(self.list_url, self.operator_token)

        ### DETAIL
        self._test_get_not_authorized(self.detail_url, self.operator_token)
        self._test_post_not_authorized(self.detail_url, self.operator_token)
        self._test_put_not_authorized(self.detail_url, self.operator_token)
        self._test_delete_not_authorized(self.detail_url, self.operator_token)
