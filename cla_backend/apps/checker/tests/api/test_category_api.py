from rest_framework.test import APITestCase

from core.tests.test_base import CLABaseApiTestMixin

from legalaid.tests.views.category_api import CategoryAPIMixin


class CategoryTestCase(CLABaseApiTestMixin, CategoryAPIMixin, APITestCase):
    API_URL_NAMESPACE = 'checker'
