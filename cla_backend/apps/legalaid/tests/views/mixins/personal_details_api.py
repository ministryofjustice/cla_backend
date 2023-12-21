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
            "contact_for_research_methods",
            "safe_to_contact",
            "vulnerable_user",
            "has_diversity",
            "announce_call"
        ]

    def _get_default_post_data(self):
        return {
            "title": "MR",
            "full_name": "John Doe",
            "postcode": "SW1H 9AJ",
            "street": "102 Petty France",
            "mobile_phone": "0123456789",
            "home_phone": "9876543210",
            "announce_call": "False"
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
                value = getattr(obj, prop)
                if value is None:
                    self.assertEqual(value, data[prop])
                else:
                    self.assertEqual(unicode(value), data[prop])
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

        data["dob"] = {"year": 1988, "month": 10, "day": 10}
        response = self._create(data=data)
        try:
            year, month, day = (
                int(response.data["dob"]["year"]),
                int(response.data["dob"]["month"]),
                int(response.data["dob"]["day"]),
            )
        except TypeError:
            self.fail("Date of birth doesn't have year, month or day")
        except ValueError:
            self.fail("Date of birth year, month and day need to be integers")

        self.assertEquals(year, data["dob"]["year"])
        self.assertEquals(month, data["dob"]["month"])
        self.assertEquals(day, data["dob"]["day"])

        # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

        self.assertPersonalDetailsEqual(response.data, check)

    def test_invalid_dob(self):
        data = self._get_default_post_data()

        data["dob"] = {"year": 1988, "month": 13, "day": 10}
        response = self._create(data=data)
        self.assertEqual(response.data["dob"], ["month must be in 1..12"])

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

    def test_personal_details_patch(self):
        data = {
            "reference": self.resource.reference,
            "title": None,
            "full_name": "John Smith",
            "postcode": "SW1H 9AJ",
            "street": "102 Petty France",
            "mobile_phone": "02033343555",
            "home_phone": "",
            "email": "test@digital.justice.gov.uk",
            "dob": {"month": "11", "day": "11", "year": "1981"},
            "ni_number": "PA102030C",
            "contact_for_research": None,
            "contact_for_research_methods": [],
            "safe_to_contact": "SAFE",
            "vulnerable_user": None,
            "has_diversity": False,
        }
        response = self._patch(data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        for key, value in data.items():
            setattr(self.resource, key, value)
        self.assertPersonalDetailsEqual(response.data, self.resource)

    def test_personal_details_patch_check_null_values(self):
        data = {
            "reference": self.resource.reference,
            "title": None,
            "full_name": None,
            "postcode": None,
            "street": None,
            "mobile_phone": None,
            "home_phone": "",
            "email": "",
            "dob": None,
            "ni_number": None,
            "contact_for_research": None,
            "contact_for_research_methods": [],
            "safe_to_contact": "SAFE",
            "vulnerable_user": None,
            "has_diversity": None,
        }
        response = self._patch(data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        for key, value in data.items():
            setattr(self.resource, key, value)
        self.assertPersonalDetailsEqual(response.data, self.resource)
        print(response)
