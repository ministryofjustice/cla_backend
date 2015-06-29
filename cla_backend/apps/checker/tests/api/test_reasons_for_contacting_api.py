from rest_framework import status
from rest_framework.test import APITestCase

from cla_common.constants import REASONS_FOR_CONTACTING
from checker.models import ReasonForContacting
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin


class ReasonsForContactingTestCase(SimpleResourceAPIMixin, CLACheckerAuthBaseApiTestMixin, APITestCase):
    LOOKUP_KEY = 'reference'
    API_URL_BASE_NAME = 'reasons_for_contacting'
    RESOURCE_RECIPE = 'checker.reasonforcontacting'

    def setUp(self):
        super(ReasonsForContactingTestCase, self).setUp()
        # give it a category as it's not auto-generated
        make_recipe('checker.reasonforcontacting_category', reason_for_contacting=self.resource)

    def test_retrieval_disallowed(self):
        self._test_get_not_allowed(self.list_url)
        self._test_get_not_allowed(self.detail_url)

    def test_create_model(self):
        resource = {
            'reasons': [{'category': REASONS_FOR_CONTACTING.OTHER}],
            'other_reasons': 'lorem ipsum',
        }
        response = self.client.post(
            self.list_url, data=resource, format='json',
            # HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['reference'])
        self.assertIsNone(response.data['case'])

    def test_can_add_case_ref(self):
        self.assertIsNone(self.resource.case)
        eligible_case = make_recipe('legalaid.eligible_case')
        response = self.client.patch(
            self.detail_url, data={'case': eligible_case.reference}, format='json',
            # HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['case'], eligible_case.reference)
        self.assertEqual(response.data['reference'], str(self.resource.reference))

    def test_stats(self):
        # only considers shared resource created during setup
        stats = ReasonForContacting.get_category_stats()
        self.assertEqual(stats['total_count'], 1)

        ideal_categories = dict((choice, 0.0) for choice in REASONS_FOR_CONTACTING.CHOICES_DICT)
        ideal_categories[self.resource.reasons.first().category] = 100.0
        categories = dict((stat['key'], stat['percentage']) for stat in stats['categories'])

        self.assertDictEqual(categories, ideal_categories)
