from lxml import objectify
from rest_framework import status
from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin

from legalaid.tests.views.mixins.provider_extract_api import ProviderExtractAPIMixin


class ProviderExtractTests(CLAProviderAuthBaseApiTestMixin, ProviderExtractAPIMixin, APITestCase):

    def test_contents_is_xmlish(self):
        """
        The extract we're copying isn't valid XML but we can still check that the
        extract we're sending is somewhat valid XML.
        """

        response = self.client.post(
            self.detail_url, data=self.get_valid_post_data(CHSCRN=self.case.reference)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        o = objectify.fromstring(response.content)

        self.assertListEqual(o.attrib.keys(), ['CRN', 'CaseCreated'])

