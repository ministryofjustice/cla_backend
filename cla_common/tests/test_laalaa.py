import unittest
import mock

from ..laalaa import LaalaaProviderCategoriesApiClient


def _laalaa_categories_endpoint_response():
    return [
        {"code": "disc", "civil": True, "name": "Discrimination"},
        {"code": "edu", "civil": True, "name": "Education"},
    ]


class LaaLaaProvidersCategoryApiClientTestCase(unittest.TestCase):
    def test_categories(self):
        api = LaalaaProviderCategoriesApiClient("", lambda s: s)
        with mock.patch.object(api, "_fetch_categories") as mock_method:
            mock_method.return_value = _laalaa_categories_endpoint_response()
            categories = api.get_categories()
            expected_categories = {category["code"]: category["name"] for category in mock_method.return_value}
            self.assertDictEqual(categories, expected_categories)

    def test_fetch_call_count(self):
        api = LaalaaProviderCategoriesApiClient("", lambda s: s)
        with mock.patch.object(api, "_fetch_categories") as mock_method:
            mock_method.return_value = _laalaa_categories_endpoint_response()
            api.get_categories()
            api.get_categories()
            api.get_categories()
            api.get_categories()
            self.assertEqual(mock_method.call_count, 1)

    def test_category_translation(self):
        translations = {"Discrimination": "foo", "Education": "bar"}

        def translator(category):
            return translations.get(category)

        api = LaalaaProviderCategoriesApiClient("", translator)
        with mock.patch.object(api, "_fetch_categories") as mock_method:
            mock_method.return_value = _laalaa_categories_endpoint_response()
            categories = api.get_categories()

            expected_categories = {"disc": "foo", "edu": "bar"}
            self.assertDictEqual(categories, expected_categories)

    def test_singleton(self):
        instance1 = LaalaaProviderCategoriesApiClient.singleton("", lambda s: s)
        instance1.foo = "bar"
        instance2 = LaalaaProviderCategoriesApiClient.singleton("", lambda s: s)
        self.assertEqual(instance2.foo, "bar")
