from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.test_base import CLACheckerAuthBaseApiTestMixin


from legalaid.tests.views.mixins.eligibility_check_api import \
    EligibilityCheckAPIMixin


class EligibilityCheckTestCase(
    CLACheckerAuthBaseApiTestMixin, EligibilityCheckAPIMixin, APITestCase
):

    def test_can_change_notes(self):
        data = {
            'notes': 'new notes',
            'your_problem_notes': 'ipsum lorem2',
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking the changed properties
        self.check.your_problem_notes = data['your_problem_notes']
        self.check.notes = data['notes']
        self.assertEligibilityCheckEqual(response.data, self.check)

    def assertEligibilityCheckEqual(self, data, check):
        self.assertEqual(data['reference'], unicode(check.reference))
        self.assertEqual(data['category'], check.category.code if check.category else None)
        self.assertEqual(data['your_problem_notes'], check.your_problem_notes)
        self.assertEqual(data['notes'], check.notes)
        self.assertEqual(len(data['property_set']), check.property_set.count())
        self.assertEqual(data['dependants_young'], check.dependants_young)
        self.assertEqual(data['dependants_old'], check.dependants_old)
        self.assertPersonEqual(data['you'], check.you)
        self.assertPersonEqual(data['partner'], check.partner)
