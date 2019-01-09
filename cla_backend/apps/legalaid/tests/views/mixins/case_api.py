from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import connection

from rest_framework import status

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin

from legalaid.models import Case
from cla_common.constants import CASE_SOURCE

from cla_eventlog.models import Log


class BaseFullCaseAPIMixin(SimpleResourceAPIMixin):
    LOOKUP_KEY = "reference"
    RESOURCE_RECIPE = "legalaid.case"
    API_URL_BASE_NAME = "case"

    def setUp(self):
        super(BaseFullCaseAPIMixin, self).setUp()

        self.list_dashboard_url = u"%s?dashboard=1" % reverse("%s:case-list" % self.API_URL_NAMESPACE)

        self.list_person_ref_url = u"%s?person_ref=1" % reverse("%s:case-list" % self.API_URL_NAMESPACE)

    def get_list_person_ref_url(self, person_ref):
        return u"%s?person_ref=%s" % (reverse("%s:case-list" % self.API_URL_NAMESPACE), person_ref)

    def get_case_serializer_clazz(self):
        raise NotImplementedError()

    def get_extra_search_make_recipe_kwargs(self):
        return {}

    @property
    def response_keys(self):
        return [
            "eligibility_check",
            "personal_details",
            "reference",
            "created",
            "modified",
            "created_by",
            "provider",
            "notes",
            "provider_notes",
            "full_name",
            "laa_reference",
            "eligibility_state",
            "adaptation_details",
            "billable_time",
            "requires_action_by",
            "matter_type1",
            "matter_type2",
            "diagnosis",
            "media_code",
            "postcode",
            "diagnosis_state",
            "thirdparty_details",
            "exempt_user",
            "exempt_user_reason",
            "ecf_statement",
            "complaint_flag",
        ]

    def assertPersonalDetailsEqual(self, data, obj):
        if isinstance(data, basestring):
            self.assertEqual(unicode(data), unicode(obj.reference))
            return
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ["title", "full_name", "postcode", "street", "mobile_phone", "home_phone"]:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])

    def assertCaseEqual(self, data, case):
        self.assertEqual(case.reference, data["reference"])

        fks = {
            "eligibility_check": "reference",
            "personal_details": "reference",
            "thirdparty_details": "reference",
            "adaptation_details": "reference",
            "diagnosis": "reference",
            "matter_type1": "code",
            "matter_type2": "code",
            "media_code": "code",
        }

        for field, fk_pk in fks.items():
            if field not in data:
                continue

            val = getattr(case, field)
            if val:
                val = unicode(getattr(val, fk_pk))
            self.assertEqual(val, data[field], "%s: %s - %s" % (field, val, data[field]))

        for field in [
            "notes",
            "billable_time",
            "laa_reference",
            "provider_notes",
            "requires_action_by",
            "exempt_user",
            "exempt_user_reason",
            "source",
        ]:
            if field not in data:
                continue

            self.assertEqual(
                getattr(case, field), data[field], "%s: %s - %s" % (field, getattr(case, field), data[field])
            )

        if "personal_details" in data:
            self.assertPersonalDetailsEqual(data["personal_details"], case.personal_details)

    def assertLogInDB(self):
        self.assertEqual(Log.objects.count(), 1)

    def assertNoLogInDB(self):
        self.assertEqual(Log.objects.count(), 0)


class FullCaseAPIMixin(BaseFullCaseAPIMixin):
    def test_case_serializer_with_eligibility_check_reference(self):
        eligibility_check = make_recipe("legalaid.eligibility_check")

        data = {u"eligibility_check": eligibility_check.reference}
        serializer = self.get_case_serializer_clazz()(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

    def test_case_serializer_with_personal_details_reference(self):
        personal_details = make_recipe(
            "legalaid.personal_details",
            **{
                u"full_name": u"John Doe",
                u"home_phone": u"9876543210",
                u"mobile_phone": u"0123456789",
                u"postcode": u"SW1H 9AJ",
                u"street": u"102 Petty France",
                u"title": u"MR",
            }
        )
        data = {u"personal_details": unicode(personal_details.reference)}

        serializer = self.get_case_serializer_clazz()(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

    def test_case_serializer_with_media_code(self):
        media_code = make_recipe("legalaid.media_code")

        data = {u"media_code": media_code.code}
        serializer = self.get_case_serializer_clazz()(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

    def test_case_serializer_with_source(self):
        data = {u"source": CASE_SOURCE.VOICEMAIL}
        serializer = self.get_case_serializer_clazz()(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})


class BaseSearchCaseAPIMixin(BaseFullCaseAPIMixin):
    def test_search_find_one_result_by_name(self):
        """
        GET search by name should work
        """
        obj = make_recipe(
            "legalaid.case",
            reference="ref1",
            personal_details__full_name="xyz",
            personal_details__postcode="123",
            **self.get_extra_search_make_recipe_kwargs()
        )

        self.resource.personal_details.full_name = "abc"
        self.resource.personal_details.postcode = "123"
        self.resource.personal_details.save()
        self.resource.reference = "ref2"
        self.resource.save()

        response = self.client.get(
            self.list_url, data={"search": "abc"}, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data["results"]))
        self.assertCaseEqual(response.data["results"][0], self.resource)

    def test_search_find_one_result_by_ref(self):
        """
        GET search by name should work
        """
        obj = make_recipe(
            "legalaid.case",
            personal_details__full_name="abc",
            personal_details__postcode="123",
            **self.get_extra_search_make_recipe_kwargs()
        )

        response = self.client.get(
            self.list_url, data={"search": self.resource.reference}, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data["results"]))
        self.assertCaseEqual(response.data["results"][0], self.resource)

    def test_search_find_one_result_by_postcode(self):
        """
        GET search by name should work
        """
        obj = make_recipe(
            "legalaid.case",
            personal_details__postcode="123",
            personal__details__full_name="abc",
            **self.get_extra_search_make_recipe_kwargs()
        )

        response = self.client.get(
            self.list_url,
            data={"search": self.resource.personal_details.postcode},
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data["results"]))
        self.assertCaseEqual(response.data["results"][0], self.resource)

    def test_search_find_none_result_by_postcode(self):
        """
        GET search by name should work
        """
        response = self.client.get(
            self.list_url,
            data={"search": self.resource.personal_details.postcode + "ss"},
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data["results"]))

    def test_search_find_none_result_by_fullname(self):
        """
        GET search by name should work
        """
        response = self.client.get(
            self.list_url,
            data={"search": self.resource.personal_details.full_name + "ss"},
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data["results"]))

    def test_search_find_none_result_by_ref(self):
        """
        GET search by name should work
        """
        response = self.client.get(
            self.list_url,
            data={"search": self.resource.reference + "ss"},
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data["results"]))


class BaseUpdateCaseTestCase(BaseFullCaseAPIMixin):
    def test_update_doesnt_set_readonly_values(self):
        _old_settings = settings.DEBUG
        try:
            settings.DEBUG = True

            pd = make_recipe("legalaid.personal_details")
            eligibility_check = make_recipe("legalaid.eligibility_check")
            thirdparty_details = make_recipe("legalaid.thirdparty_details")
            adaptation_details = make_recipe("legalaid.adaptation_details")
            diagnosis = make_recipe("diagnosis.diagnosis")
            provider = make_recipe("cla_provider.provider")

            case = make_recipe(
                "legalaid.case",
                eligibility_check=eligibility_check,
                personal_details=pd,
                thirdparty_details=thirdparty_details,
                adaptation_details=adaptation_details,
                diagnosis=diagnosis,
                media_code=None,
                matter_type1=None,
                matter_type2=None,
                source=CASE_SOURCE.PHONE,
                **self.get_extra_search_make_recipe_kwargs()
            )

            media_code = make_recipe("legalaid.media_code")

            matter_type1 = make_recipe("legalaid.matter_type1")
            matter_type2 = make_recipe("legalaid.matter_type2")

            data = {
                "personal_details": None,
                "eligibility_check": None,
                "thirdparty_details": None,
                "adaptation_details": None,
                "diagnosis": None,
                "provider": None,
                "billable_time": 234,
                "created": "2014-08-05T10:41:55.979Z",
                "modified": "2014-08-05T10:41:55.985Z",
                "created_by": "test_user",
                "matter_type1": matter_type1.code,
                "matter_type2": matter_type2.code,
                "media_code": media_code.code,
                "laa_reference": 232323,
                "source": CASE_SOURCE.VOICEMAIL,
                "requires_action_by": REQUIRES_ACTION_BY.PROVIDER_REVIEW,
            }
            response = self.client.patch(
                self.get_detail_url(case.reference),
                data=data,
                format="json",
                HTTP_AUTHORIZATION=self.get_http_authorization(),
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertResponseKeys(response)

            self.assertCaseEqual(
                response.data,
                Case(
                    reference=response.data["reference"],
                    personal_details=pd,
                    eligibility_check=eligibility_check,
                    thirdparty_details=thirdparty_details,
                    adaptation_details=adaptation_details,
                    diagnosis=diagnosis,
                    provider=provider,
                    billable_time=0,
                    laa_reference=response.data["laa_reference"],
                    matter_type1=matter_type1,
                    matter_type2=matter_type2,
                    media_code=media_code,
                    source=CASE_SOURCE.VOICEMAIL,
                    requires_action_by=case.requires_action_by,
                ),
            )

            self.assertNotEqual(response.data["requires_action_by"], data["requires_action_by"])
            self.assertNotEqual(response.data["created"], data["created"])
            self.assertNotEqual(response.data["created_by"], data["created_by"])
            self.assertNotEqual(response.data["modified"], data["modified"])
            self.assertNotEqual(response.data["laa_reference"], data["laa_reference"])

            self.assertNoLogInDB()

            # looking for the update case query
            update_query = [query for query in connection.queries if query["sql"].startswith("UPDATE")]
            self.assertEqual(len(update_query), 1)
            update_sql = update_query[0]["sql"]

            for readonly_field in [
                "personal_details",
                "eligibility_check",
                "thirdparty_details",
                "adaptation_details",
                "provider",
                "billable_time",
                "laa_reference",
                "requires_action_by",
            ]:
                self.assertFalse(
                    readonly_field in update_sql, "%s is in the UPDATE query when it shouldn't be!" % readonly_field
                )
        finally:
            settings.DEBUG = _old_settings
            connection.queries = []

    def test_update_with_data(self):
        media_code = make_recipe("legalaid.media_code")
        matter_type1 = make_recipe("legalaid.matter_type1")
        matter_type2 = make_recipe("legalaid.matter_type2")

        data = {
            "matter_type1": matter_type1.code,
            "matter_type2": matter_type2.code,
            "media_code": media_code.code,
            "source": CASE_SOURCE.VOICEMAIL,
        }
        response = self.client.patch(self.detail_url, data=data, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseKeys(response)

        case = self.resource
        case.matter_type1 = matter_type1
        case.matter_type2 = matter_type2
        case.media_code = media_code
        case.source = CASE_SOURCE.VOICEMAIL
        self.assertCaseEqual(response.data, case)

        self.assertNoLogInDB()

    def test_complaint_flag_update_creates_log(self):
        data = {"complaint_flag": True}

        log_count = Log.objects.count()
        response = self.client.patch(self.detail_url, data=data, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Log.objects.count(), log_count + 1)
        log = Log.objects.all().first()
        self.assertEqual(log.code, "COMPLAINT_FLAG_TOGGLED")
        self.assertTrue(log.notes.endswith("True"))
