from rest_framework.test import APITestCase

from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin


class CSVUploadAPIMixin(SimpleResourceAPIMixin):
    RESOURCE_RECIPE = 'cla_provider.csvupload_case'
    API_URL_BASE_NAME = 'csvupload'

    @property
    def response_keys(self):
        return [
            'id',
            'provider',
            'created_by',
            'comment',
            'rows',
            'month',
            'created',
        ]

    @property
    def response_keys_details(self):
        keys = self.response_keys[:]
        keys.remove('rows')
        keys.append('body')
        return keys




class CSVUploadTestCase(CSVUploadAPIMixin,
                        CLAOperatorAuthBaseApiTestMixin,
                        APITestCase):


    def assertResponseKeys(self, response, detail=False):
        return \
            super(CSVUploadTestCase, self).assertResponseKeys(
                response,
                keys=self.response_keys_details if detail else None)

    def test_get(self):
        response = self.client.get(
            self.detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization(self.operator_manager_token)
        )

        self.assertResponseKeys(
            response, detail=True
        )

    def test_get_list(self):
        response = \
            self.client.get(self.list_url,
                            HTTP_AUTHORIZATION=self.get_http_authorization(self.operator_manager_token))

        self.assertResponseKeys(response)

    def test_methods_not_authorized(self):
        self._test_get_not_authorized(self.list_url, self.invalid_token)
        self._test_get_not_authorized(self.detail_url, self.invalid_token)


