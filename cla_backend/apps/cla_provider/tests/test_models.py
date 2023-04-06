from django.test import TestCase
from django.db import IntegrityError
from core.tests.mommy_utils import make_recipe


class ProviderModelTestCase(TestCase):
    def test_unique_provider_name(self):
        make_recipe("cla_provider.provider", name="Stephensons")
        with self.assertRaises(IntegrityError):
            make_recipe("cla_provider.provider", name="Stephensons")
