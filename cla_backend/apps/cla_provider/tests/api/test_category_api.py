from rest_framework.test import APITestCase

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin

from legalaid.tests.views.category_api import CategoryAPIMixin


class CategoryTestCase(CategoryAPIMixin, CLAProviderAuthBaseApiTestMixin, APITestCase):
    def get_http_authorization(self):
        return 'Bearer %s' % self.token
