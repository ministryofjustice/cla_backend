import uuid
from core.tests.mommy_utils import make_recipe
from rest_framework import status
from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin


from legalaid.tests.views.mixins.eligibility_check_api import EligibilityCheckAPIMixin


class EligibilityCheckTestCase(EligibilityCheckAPIMixin, CLACheckerAuthBaseApiTestMixin, APITestCase):
    def test_can_change_notes(self):
        data = {"notes": "new notes", "your_problem_notes": "ipsum lorem2"}
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking the changed properties
        self.resource.your_problem_notes = data["your_problem_notes"]
        self.resource.notes = data["notes"]
        self.assertEligibilityCheckEqual(response.data, self.resource)

    def assertEligibilityCheckEqual(self, data, check):
        self.assertEqual(data["reference"], unicode(check.reference))
        self.assertEqual(data["category"], check.category.code if check.category else None)
        self.assertEqual(data["your_problem_notes"], check.your_problem_notes)
        self.assertEqual(data["notes"], check.notes)
        self.assertEqual(len(data["property_set"]), check.property_set.count())
        self.assertEqual(data["dependants_young"], check.dependants_young)
        self.assertEqual(data["dependants_old"], check.dependants_old)
        self.assertPersonEqual(data["you"], check.you)
        self.assertPersonEqual(data["partner"], check.partner, partner=True)

    def test_case_ref_api(self):
        case = make_recipe("legalaid.case")

        case.eligibility_check = self.resource
        case.save()

        case_ref_url = u"%s%s" % (self.detail_url, u"case_ref/")

        response = self.client.get(case_ref_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        case_ref_url = case_ref_url.replace(unicode(self.resource_lookup_value), unicode(uuid.uuid1()))

        response = self.client.get(case_ref_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Checker doesn't send updates for partner financial details
    def test_patch_with_no_partner_finances(self):
        pass

    def test_patch_with_no_partner_income(self):
        pass

    # Checker doesn't passport under 18s
    def test_eligibility_check_under_18(self):
        pass

    # Checker doesn't send updates for partner financial details
    def test_with_null_partner_self_employed(self):
        pass
