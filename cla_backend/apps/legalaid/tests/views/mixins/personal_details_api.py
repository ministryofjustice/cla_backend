from rest_framework import status

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import NestedSimpleResourceAPIMixin

from legalaid.utils import diversity


class PersonalDetailsAPIMixin(NestedSimpleResourceAPIMixin):
    LOOKUP_KEY = "case_reference"
    PARENT_LOOKUP_KEY = "reference"
    API_URL_BASE_NAME = "personaldetails"
    RESOURCE_RECIPE = "legalaid.personal_details"
    PARENT_RESOURCE_RECIPE = "legalaid.case"
    PK_FIELD = "personal_details"

    @property
    def response_keys(self):
        return [
            "reference",
            "title",
            "full_name",
            "postcode",
            "street",
            "mobile_phone",
            "home_phone",
            "email",
            "dob",
            "ni_number",
            "contact_for_research",
            "contact_for_research_via",
            "safe_to_contact",
            "vulnerable_user",
            "has_diversity",
        ]

    def _get_default_post_data(self):
        return {
            "title": "MR",
            "full_name": "John Doe",
            "postcode": "SW1H 9AJ",
            "street": "102 Petty France",
            "mobile_phone": "0123456789",
            "home_phone": "9876543210",
        }

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        data = {
            "title": "1" * 21,
            "full_name": "1" * 456,
            "postcode": "1" * 13,
            "street": "1" * 256,
            "mobile_phone": "1" * 21,
            "home_phone": "1" * 21,
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_errors = {
            "title": [u"Ensure this value has at most 20 characters (it has 21)."],
            "full_name": [u"Ensure this value has at most 400 characters (it has 456)."],
            "postcode": [u"Ensure this value has at most 12 characters (it has 13)."],
            "street": [u"Ensure this value has at most 255 characters (it has 256)."],
            "mobile_phone": [u"Ensure this value has at most 20 characters (it has 21)."],
            "home_phone": [u"Ensure this value has at most 20 characters (it has 21)."],
        }

        self.maxDiff = None
        errors = response.data
        self.assertItemsEqual(errors.keys(), expected_errors.keys())
        self.assertItemsEqual(errors, expected_errors)

    def assertPersonalDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ["title", "full_name", "postcode", "street", "mobile_phone", "home_phone"]:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])
            self.assertEqual(data["has_diversity"], bool(obj.diversity))

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # LIST
        if hasattr(self, "list_url") and self.list_url:
            self._test_delete_not_allowed(self.list_url)

    def test_methods_in_error(self):
        self._test_method_in_error("patch", self.detail_url)
        self._test_method_in_error("put", self.detail_url)

        # CREATE

    def test_create_no_data(self):
        """
        CREATE should work, even with an empty POST
        """
        response = self._create()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

    def test_create_with_data(self):
        data = self._get_default_post_data()
        check = make_recipe("legalaid.personal_details", **data)

        response = self._create(data=data)
        # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

        self.assertPersonalDetailsEqual(response.data, check)

    # GET

    def test_get(self):
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertPersonalDetailsEqual(response.data, self.parent_resource.personal_details)

    def test_get_with_diversity(self):
        diversity.save_diversity_data(self.resource.pk, {"key": "test_data"})
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.resource = self.resource.__class__.objects.get(pk=self.resource.pk)
        self.assertPersonalDetailsEqual(response.data, self.resource)
        self.assertEqual(response.data["has_diversity"], True)
