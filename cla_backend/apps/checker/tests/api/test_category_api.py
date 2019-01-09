from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin

from legalaid.tests.views.mixins.category_api import CategoryAPIMixin


class CategoryTestCase(CLACheckerAuthBaseApiTestMixin, CategoryAPIMixin, APITestCase):
    pass
