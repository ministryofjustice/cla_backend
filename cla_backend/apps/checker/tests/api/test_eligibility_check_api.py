from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.test_base import CLABaseApiTestMixin


from legalaid.tests.views.eligibility_check_api import EligibilityCheckAPIMixin


class EligibilityCheckTestCase(CLABaseApiTestMixin, EligibilityCheckAPIMixin, APITestCase):
    API_URL_NAMESPACE = 'checker'

    def test_can_change_notes(self):
        data={
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
