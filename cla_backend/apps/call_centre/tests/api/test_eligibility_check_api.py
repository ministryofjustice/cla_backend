from rest_framework import status
from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from legalaid.tests.views.mixins.eligibility_check_api import NestedEligibilityCheckAPIMixin

from legalaid.models import EligibilityCheck, Person, Savings
from cla_eventlog.models import Log


class EligibilityCheckTestCase(CLAOperatorAuthBaseApiTestMixin, NestedEligibilityCheckAPIMixin, APITestCase):
    LOOKUP_KEY = "case_reference"

    @property
    def response_keys(self):
        return [
            "reference",
            "category",
            "notes",
            "your_problem_notes",
            "property_set",
            "dependants_young",
            "dependants_old",
            "you",
            "partner",
            "disputed_savings",
            "has_partner",
            "on_passported_benefits",
            "on_nass_benefits",
            "is_you_or_your_partner_over_60",
            "state",
            "specific_benefits",
            "disregards",
            "has_passported_proceedings_letter",
        ]

    def test_notes_are_readonly(self):
        data = {"notes": "just trying...", "your_problem_notes": "ipsum lorem2"}
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking the changed properties
        self.resource.your_problem_notes = data["your_problem_notes"]
        self.assertEligibilityCheckEqual(response.data, self.resource)
        self.assertTrue(response.data["notes"] != data["notes"])

    def test_empty_fields(self):
        """
        When patching a NullBooleanField setting it to None, DRF saves it
        as None value.
        """
        data = {
            "category": None,
            "dependants_old": None,
            "dependants_young": None,
            "has_partner": None,
            "is_you_or_your_partner_over_60": None,
            "notes": "",
            "on_nass_benefits": None,
            "on_passported_benefits": None,
            "partner": None,
            "property_set": [],
            "state": "unknown",
            "you": None,
            "disputed_savings": None,
            "your_problem_notes": "",
        }
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        # TODO: needs more checks

        self.assertEqual(response.data["has_partner"], None)
        self.assertEqual(response.data["is_you_or_your_partner_over_60"], None)

    def test_check_validate_api_method_works(self):
        # actual testing of 'validate' is done in model tests.
        response = self.client.get(
            self.detail_url + "validate/", {}, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"warnings": {}})

    def test_check_validate_disregards(self):
        """
               Make sure that the disregards does not allow fields that have not been created
               """
        disregard_defined = {"disregards": {"criminal_injuries": "true"}}

        disregard_not_defined = {"disregards": {"no_disregard_defined": "true"}}

        response = self.client.patch(
            self.detail_url, data=disregard_defined, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        # if you pass in  an expected disregards field then it should return the same data
        expected_good = {"criminal_injuries": True}
        self.assertEqual(response.data["disregards"], expected_good)

        # if you pass in something other than an expected disregards field then it should fail
        response = self.client.patch(
            self.detail_url,
            data=disregard_not_defined,
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        expected_bad = {"disregards": [u"Fields no_disregard_defined not recognised"]}
        self.assertEqual(response.data, expected_bad)

    def test_create_with_finances_and_check_log(self):
        """
        CREATE data with finances
        """
        data = self._get_valid_post_data()
        response = self._create(data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure the "MT_CREATED" log entry is created
        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(Log.objects.all().first().code, "MT_CREATED")

        self.assertResponseKeys(response)
        self.assertEligibilityCheckEqual(
            response.data,
            EligibilityCheck(
                reference=response.data["reference"],
                you=Person.from_dict(data["you"]),
                partner=Person.from_dict(data["partner"]),
                disputed_savings=Savings(
                    bank_balance=1111, investment_balance=2222, asset_balance=3333, credit_balance=4444
                ),
            ),
        )

    def test_patch_add_disputed_savings(self):
        """
        Patch data with finances
        """
        data = {
            "reference": self.resource.reference,
            "disputed_savings": {
                "bank_balance": 1111,
                "investment_balance": 2222,
                "asset_balance": 3333,
                "credit_balance": 4444,
            },
        }
        response = self._update(ref=self.resource.case.reference, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertResponseKeys(response)
        self.assertSavingsEqual(
            response.data["disputed_savings"],
            Savings(bank_balance=1111, investment_balance=2222, asset_balance=3333, credit_balance=4444),
        )
