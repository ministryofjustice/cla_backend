import datetime
from itertools import cycle
from rest_framework import status
from rest_framework.test import APITestCase

from cla_common.constants import REASONS_FOR_CONTACTING
from checker.models import ReasonForContacting
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin


class ReasonsForContactingTestCase(SimpleResourceAPIMixin, CLACheckerAuthBaseApiTestMixin, APITestCase):
    LOOKUP_KEY = "reference"
    API_URL_BASE_NAME = "reasons_for_contacting"
    RESOURCE_RECIPE = "checker.reasonforcontacting"

    def setUp(self):
        super(ReasonsForContactingTestCase, self).setUp()
        # give it a category as it's not auto-generated
        make_recipe("checker.reasonforcontacting_category", reason_for_contacting=self.resource)
        self.date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        self.date_to = datetime.datetime.now() + datetime.timedelta(days=1)
        self.referrers = [
            "Unknown",
            "https://localhost/scope/diagnosis",
            "https://localhost/scope/diagnosis/n131",
            "https://localhost/scope/diagnosis?category=check",
            "https://localhost/scope/diagnosis",
        ]

    def test_retrieval_disallowed(self):
        self._test_get_not_allowed(self.list_url)
        self._test_get_not_allowed(self.detail_url)

    def test_create_model(self):
        resource = {"reasons": [{"category": REASONS_FOR_CONTACTING.OTHER}], "other_reasons": "lorem ipsum"}
        response = self.client.post(
            self.list_url,
            data=resource,
            format="json",
            # HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["reference"])
        self.assertIsNone(response.data["case"])

    def test_can_add_case_ref(self):
        self.assertIsNone(self.resource.case)
        eligible_case = make_recipe("legalaid.eligible_case")
        response = self.client.patch(
            self.detail_url,
            data={"case": eligible_case.reference},
            format="json",
            # HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["case"], eligible_case.reference)
        self.assertEqual(response.data["reference"], str(self.resource.reference))

    def test_stats(self):
        # only considers shared resource created during setup
        stats = ReasonForContacting.get_category_stats()
        self.assertEqual(stats["total_count"], 1)

        ideal_categories = dict((choice, 0.0) for choice in REASONS_FOR_CONTACTING.CHOICES_DICT)
        ideal_categories[self.resource.reasons.first().category] = 100.0
        categories = dict((stat["key"], stat["percentage"]) for stat in stats["categories"])

        self.assertDictEqual(categories, ideal_categories)

    def test_report_stats_referrer(self):
        resources = make_recipe("checker.reasonforcontacting", referrer=cycle(self.referrers), _quantity=5)
        # create the associated categories and check number of results returned
        for resource in resources:
            make_recipe("checker.reasonforcontacting_category", reason_for_contacting=resource)
            ref = resource.referrer
            stats = ReasonForContacting.get_report_category_stats(
                start_date=self.date_from, end_date=self.date_to, referrer=ref
            )
            self.assertEqual(stats["total_count"], self.referrers.count(ref))

    def test_report_stats_dates_with_no_results(self):
        # all created resources will have today's date
        past_date_from = datetime.datetime.now() - datetime.timedelta(days=5)
        past_date_to = datetime.datetime.now() - datetime.timedelta(days=4)
        stats = ReasonForContacting.get_report_category_stats(start_date=past_date_from, end_date=past_date_to)
        self.assertEqual(stats["total_count"], 0)

    def test_report_stats_dates_with_results(self):
        # don't forget about the one original resource from setup
        resources = make_recipe("checker.reasonforcontacting", referrer=cycle(self.referrers), _quantity=5)
        # create the associated categories and check number of results returned
        for resource in resources:
            make_recipe("checker.reasonforcontacting_category", reason_for_contacting=resource)
        stats = ReasonForContacting.get_report_category_stats(start_date=self.date_from, end_date=self.date_to)
        self.assertEqual(stats["total_count"], 6)
