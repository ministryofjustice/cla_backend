import datetime
import uuid

import mock
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from cla_common.constants import CASE_SOURCE
from cla_eventlog.models import Log
from checker.serializers import CaseSerializer
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.models import Case, PersonalDetails, ThirdPartyDetails, AdaptationDetails
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin
from call_centre.tests.test_utils import CallCentreFixedOperatingHours
from cla_provider.tests.test_notify import MockGovNotifyMailBox


class BaseCaseTestCase(
    MockGovNotifyMailBox,
    CLACheckerAuthBaseApiTestMixin,
    CallCentreFixedOperatingHours,
    SimpleResourceAPIMixin,
    APITestCase,
):
    LOOKUP_KEY = "reference"
    API_URL_BASE_NAME = "case"
    RESOURCE_RECIPE = "legalaid.case"

    def make_resource(self):
        return None

    def assertCaseResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            [
                "eligibility_check",
                "personal_details",
                "reference",
                "requires_action_at",
                "callback_window_type",
                "adaptation_details",
                "thirdparty_details",
            ],
        )

    def assertPersonalDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ["title", "full_name", "postcode", "street", "mobile_phone", "home_phone"]:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])

    def assertThirdPartyDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            self.assertEqual(data["personal_relationship"], obj.personal_relationship)
            for prop in ["full_name", "mobile_phone", "safe_to_contact"]:
                self.assertEqual(unicode(getattr(obj.personal_details, prop)), data["personal_details"][prop])

    def assertCaseEqual(self, data, case):
        self.assertEqual(case.reference, data["reference"])
        self.assertEqual(unicode(case.eligibility_check.reference), data["eligibility_check"])
        self.assertPersonalDetailsEqual(data["personal_details"], case.personal_details)
        self.assertThirdPartyDetailsEqual(data["thirdparty_details"], case.thirdparty_details)
        self.assertAdaptationDetailsEqual(data["adaptation_details"], case.adaptation_details)

        self.assertEqual(Case.objects.count(), 1)
        case = Case.objects.first()
        self.assertEqual(case.source, CASE_SOURCE.WEB)

    def assertAdaptationDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ["language"]:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])

    def get_personal_details_default_post_data(self):
        return {
            "title": "MR",
            "full_name": "John Doe",
            "postcode": "SW1H 9AJ",
            "street": "102 Petty France",
            "mobile_phone": "0123456789",
            "home_phone": "9876543210",
        }

    def get_thirdparty_details_default_post_data(self):
        return {
            "personal_details": {"full_name": "Jo Bloggs", "mobile_phone": "02081234567", "safe_to_contact": "SAFE"},
            "personal_relationship": "FAMILY_FRIEND",
        }


class CaseTestCase(BaseCaseTestCase):
    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # LIST
        self._test_delete_not_allowed(self.list_url)

    # CREATE

    def test_create_no_data(self):
        """
        CREATE should raise validation error when data is empty
        """
        response = self.client.post(self.list_url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertItemsEqual(response.data.keys(), ["personal_details"])

        self.assertEqual(Case.objects.count(), 0)

    def test_adaptation_details(self):
        language_list = ["ARABIC", u""]

        for language in language_list:
            check = make_recipe("legalaid.eligibility_check")

            data = {
                "eligibility_check": unicode(check.reference),
                "personal_details": self.get_personal_details_default_post_data(),
                "adaptation_details": {
                    "text_relay": False,
                    "notes": "",
                    "bsl_webcam": False,
                    "language": language,
                    "minicom": False,
                },
            }
            response = self.client.post(self.list_url, data=data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data["adaptation_details"]["language"], language)

    def test_adaptation_details_empty_string(self):
        check = make_recipe("legalaid.eligibility_check")

        data = {
            "eligibility_check": unicode(check.reference),
            "personal_details": self.get_personal_details_default_post_data(),
            "adaptation_details": {
                "text_relay": False,
                "notes": "",
                "bsl_webcam": False,
                "language": u"",
                "minicom": False,
            },
        }

        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["adaptation_details"]["language"])
        self.assertEqual(response.data["adaptation_details"]["language"], u"")

    def test_adaptation_details_language_added(self):
        check = make_recipe("legalaid.eligibility_check")

        data = {
            "eligibility_check": unicode(check.reference),
            "personal_details": self.get_personal_details_default_post_data(),
            "adaptation_details": {
                "text_relay": False,
                "notes": "",
                "bsl_webcam": False,
                "language": "ARABIC",
                "minicom": False,
            },
        }

        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["adaptation_details"]["language"], "ARABIC")

    def test_adaptation_details_language_missing(self):
        check = make_recipe("legalaid.eligibility_check")

        data = {
            "eligibility_check": unicode(check.reference),
            "personal_details": self.get_personal_details_default_post_data(),
            "adaptation_details": {"text_relay": False, "notes": "", "bsl_webcam": False, "minicom": False},
        }

        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["adaptation_details"]["language"])

    def test_create_with_data(self):
        check = make_recipe("legalaid.eligibility_check")

        data = {
            "eligibility_check": unicode(check.reference),
            "personal_details": self.get_personal_details_default_post_data(),
            "thirdparty_details": self.get_thirdparty_details_default_post_data(),
            "adaptation_details": {
                "text_relay": False,
                "notes": "",
                "bsl_webcam": False,
                "language": u"",
                "minicom": False,
            },
        }
        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

        # third party personal details needs to be converted to an object
        data["thirdparty_details"]["personal_details"] = PersonalDetails(
            **data["thirdparty_details"]["personal_details"]
        )
        self.assertCaseEqual(
            response.data,
            Case(
                reference=response.data["reference"],
                eligibility_check=check,
                personal_details=PersonalDetails(**data["personal_details"]),
                thirdparty_details=ThirdPartyDetails(**data["thirdparty_details"]),
                adaptation_details=AdaptationDetails(**data["adaptation_details"]),
            ),
        )

        # test that the Case is in the db and created by 'web' user
        self.assertEqual(Case.objects.count(), 1)
        case = Case.objects.first()
        self.assertEqual(case.created_by.username, "web")

        # test that the log is in the db and created by 'web' user
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.first()
        self.assertEqual(log.created_by.username, "web")

        # no email sent
        self.assertEquals(len(self.mailbox), 0)

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        invalid_uuid = str(uuid.uuid4())
        data = {
            "eligibility_check": invalid_uuid,
            "personal_details": {
                "title": "1" * 21,
                "full_name": None,
                "postcode": "1" * 13,
                "street": "1" * 256,
                "mobile_phone": "1" * 21,
                "home_phone": "1" * 21,
            },
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data
        self.assertItemsEqual(errors.keys(), ["eligibility_check", "personal_details"])
        self.assertEqual(errors["eligibility_check"], [u"Object with reference=%s does not exist." % invalid_uuid])
        self.assertDictEqual(
            errors["personal_details"],
            {
                "title": [u"Ensure this field has no more than 20 characters."],
                "postcode": [u"Ensure this field has no more than 12 characters."],
                "street": [u"Ensure this field has no more than 255 characters."],
                "mobile_phone": [u"Ensure this field has no more than 20 characters."],
                "home_phone": [u"Ensure this field has no more than 20 characters."],
            },
        )

    def test_create_in_error(self):
        self._test_method_in_error("post", self.list_url)

    def test_cannot_create_with_other_reference(self):
        """
        Cannot create a case passing an eligibility check reference already assigned
        to another case
        """
        # create a different case
        case = make_recipe("legalaid.case")

        data = {
            "eligibility_check": unicode(case.eligibility_check.reference),
            "personal_details": self.get_personal_details_default_post_data(),
        }
        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data, {"eligibility_check": [u"Case with this Eligibility check already exists."]}
        )

    def test_case_serializer_with_dupe_eligibility_check_reference(self):
        case = make_recipe("legalaid.case")

        data = {
            u"eligibility_check": case.eligibility_check.reference,
            u"personal_details": self.get_personal_details_default_post_data(),
        }
        serializer = CaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertDictEqual(
            serializer.errors, {"eligibility_check": [u"Case with this Eligibility check already exists."]}
        )


class CallMeBackCaseTestCase(BaseCaseTestCase):
    @property
    def _default_dt(self):
        if not hasattr(self, "__default_dt"):
            self.__default_dt = datetime.datetime(2015, 3, 30, 10, 0, 0, 0).replace(tzinfo=timezone.utc)
        return self.__default_dt

    def test_create_with_callmeback(self):
        self.assertEquals(len(self.mailbox), 0)

        check = make_recipe("legalaid.eligibility_check")

        data = {
            "eligibility_check": unicode(check.reference),
            "personal_details": self.get_personal_details_default_post_data(),
            "requires_action_at": self._default_dt.isoformat(),
        }
        with mock.patch(
            "cla_common.call_centre_availability.current_datetime",
            return_value=datetime.datetime(2015, 3, 23, 10, 0, 0, 0),
        ):
            response = self.client.post(self.list_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

        case = Case.objects.first()
        self.assertEqual(case.requires_action_at, self._default_dt)
        self.assertEqual(case.callback_attempt, 1)
        self.assertEqual(case.outcome_code, "CB1")
        self.assertEqual(case.source, CASE_SOURCE.WEB)
        self.assertEqual(case.log_set.count(), 2)

        self.assertEqual(case.log_set.filter(code="CB1").count(), 1)
        log = case.log_set.get(code="CB1")

        self.assertEqual(
            log.notes,
            "Callback scheduled for %s - %s. "
            % (
                timezone.localtime(self._default_dt).strftime("%d/%m/%Y %H:%M"),
                (timezone.localtime(self._default_dt) + datetime.timedelta(minutes=30)).strftime("%H:%M"),
            ),
        )
        _dt = timezone.localtime(self._default_dt)
        expected_sla_72h = datetime.datetime(2015, 4, 7, 13, 30, 0, 0)
        self.assertDictEqual(
            log.context,
            {
                "requires_action_at": _dt.isoformat(),
                "sla_120": (_dt + datetime.timedelta(minutes=120)).isoformat(),
                "sla_480": (_dt + datetime.timedelta(hours=8)).isoformat(),
                "sla_15": (_dt + datetime.timedelta(minutes=15)).isoformat(),
                "sla_30": (_dt + datetime.timedelta(minutes=30)).isoformat(),
                "sla_72h": timezone.make_aware(expected_sla_72h, _dt.tzinfo).isoformat(),
            },
        )

        # checking email
        self.assertEquals(len(self.mailbox), 1)

        # Check that logs are created in order
        first = Log.objects.order_by("-created").first()
        self.assertEqual("CB1", first.code)
        last = Log.objects.order_by("-created").last()
        self.assertEqual("CASE_CREATED", last.code)

    def test_create_should_ignore_outcome_code(self):
        """
        Here only to check backward incompatibility
        """
        check = make_recipe("legalaid.eligibility_check")

        data = {
            "eligibility_check": unicode(check.reference),
            "personal_details": self.get_personal_details_default_post_data(),
            "requires_action_at": self._default_dt.isoformat(),
            "outcome_code": "TEST",
        }
        response = self.client.post(self.list_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

        case = Case.objects.first()
        self.assertNotEqual(case.outcome_code, "TEST")
