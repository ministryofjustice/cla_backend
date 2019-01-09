from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from legalaid.tests.views.mixins.category_api import CategoryAPIMixin


class CategoryTestCase(CLAOperatorAuthBaseApiTestMixin, CategoryAPIMixin, APITestCase):
    pass
