from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from legalaid.tests.views.mixins.category_api import CategoryAPIMixin


class CategoryTestCase(
    CategoryAPIMixin, CLAOperatorAuthBaseApiTestMixin, APITestCase
):
    pass
