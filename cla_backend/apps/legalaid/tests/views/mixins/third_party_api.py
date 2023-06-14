from rest_framework import status

from core.tests.test_base import NestedSimpleResourceAPIMixin


class ThirdPartyDetailsApiMixin(NestedSimpleResourceAPIMixin):
    LOOKUP_KEY = "case_reference"
    RESOURCE_RECIPE = "legalaid.thirdparty_details"
    API_URL_BASE_NAME = "thirdpartydetails"
    PARENT_LOOKUP_KEY = "reference"
    PARENT_RESOURCE_RECIPE = "legalaid.case"
    PK_FIELD = "thirdparty_details"

    @property
    def response_keys(self):
        return [
            "reference",
            "personal_details",
            "pass_phrase",
            "reason",
            "personal_relationship",
            "personal_relationship_note",
            "spoke_to",
            "no_contact_reason",
            "organisation_name",
        ]

    def _get_default_post_data(self):
        return {
            "personal_details": {
                "title": "Mr",
                "full_name": "Bob",
                "postcode": "SW1H 9AJ",
                "street": "102 Petty France",
                "mobile_phone": "07000000000",
                "home_phone": "01179000000",
            },
            "pass_phrase": "monkey",
            "reason": "CHILD_PATIENT",
            "personal_relationship": "OTHER",
            "personal_relationship_note": "Neighbour",
        }

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        data = {
            "personal_details": {
                "title": "1" * 21,
                "full_name": "1" * 456,
                "postcode": "1" * 13,
                "street": "1" * 256,
                "mobile_phone": "1" * 21,
                "home_phone": "1" * 21,
            },
            "pass_phrase": "XXXXXXXXX",
            "reason": "XXXXXXXXX",
            "personal_relationship": "XXXXXXXXX",
            "personal_relationship_note": "XXXXXXXX",
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, HTTP_AUTHORIZATION=self.get_http_authorization(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_errors = {
            "personal_details": {
                "full_name": [u"Ensure this field has no more than 400 characters."],
                "home_phone": [u"Ensure this field has no more than 20 characters."],
                "mobile_phone": [u"Ensure this field has no more than 20 characters."],
                "postcode": [u"Ensure this field has no more than 12 characters."],
                "street": [u"Ensure this field has no more than 255 characters."],
                "title": [u"Ensure this field has no more than 20 characters."],
            },
            "reason": [u'"XXXXXXXXX" is not a valid choice.'],
            "personal_relationship": [u'"XXXXXXXXX" is not a valid choice.'],
        }

        errors = response.data
        self.assertItemsEqual(errors.keys(), expected_errors.keys())
        self.assertDictEqual(errors, expected_errors)

    def assertThirdPartyDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ["pass_phrase", "reason", "personal_relationship", "personal_relationship_note"]:
                if isinstance(obj, dict):
                    val = obj[prop]
                else:
                    val = getattr(obj, prop)
                    if val:
                        val = unicode(val)
                self.assertEqual(val, data[prop])

    def test_methods_not_allowed(self):
        """
        Ensure that we can't DELETE to list url
        """
        # LIST
        if hasattr(self, "list_url") and self.list_url:
            self._test_delete_not_allowed(self.list_url)

    def test_methods_in_error(self):
        self._test_method_in_error("patch", self.detail_url)
        self._test_method_in_error("put", self.detail_url)

    # CREATE

    def test_create_with_data(self):
        """
        check variables sent as same as those that return.
        """
        data = self._get_default_post_data()
        check = self._get_default_post_data()

        response = self._create(data=data)
        # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

        self.assertThirdPartyDetailsEqual(response.data, check)

    def test_update_with_data(self):
        """
        check variables sent as same as those that return.
        """
        data = self._get_default_post_data()
        data["reference"] = self.resource.reference
        data["personal_details"]["postcode"] = "SW3H 9AJ"
        data["pass_phrase"] = "banana"

        check = self._get_default_post_data()
        check["reference"] = self.resource.reference
        check["personal_details"]["postcode"] = "SW3H 9AJ"
        check["pass_phrase"] = "banana"

        response = self.client.patch(
            self.detail_url, data=data or {}, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        # check state is correct

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseKeys(response)
        self.assertThirdPartyDetailsEqual(response.data, check)

    # GET

    def test_get(self):
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertThirdPartyDetailsEqual(response.data, self.parent_resource.thirdparty_details)
