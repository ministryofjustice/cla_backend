from rest_framework.test import APITestCase

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin

from legalaid.tests.views.mixins.category_api import CategoryAPIMixin


class CategoryTestCase(
    CategoryAPIMixin, CLAProviderAuthBaseApiTestMixin, APITestCase
):
    pass
