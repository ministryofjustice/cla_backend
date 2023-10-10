import datetime

from dateutil.parser import parse
from django.core.urlresolvers import reverse
from django.utils import timezone
import mock
from rest_framework.test import APITestCase
from rest_framework import status
from cla_provider.helpers import ProviderAllocationHelper
from cla_provider.tests.test_notify import MockGovNotifyMailBox

from legalaid.models import Case, CaseNotesHistory
from legalaid.tests.views.mixins.case_api import (
    BaseFullCaseAPIMixin,
    FullCaseAPIMixin,
    BaseSearchCaseAPIMixin,
    BaseUpdateCaseTestCase,
)
from cla_common.constants import CASE_SOURCE, REQUIRES_ACTION_BY

from cla_eventlog.models import Log
from cla_eventlog.tests.test_views import ExplicitEventCodeViewTestCaseMixin, ImplicitEventCodeViewTestCaseMixin

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe

from call_centre.forms import DeclineHelpCaseForm, SuspendCaseForm
from call_centre.serializers import CaseSerializer, ProviderSerializer


class BaseCaseTestCase(CLAOperatorAuthBaseApiTestMixin, BaseFullCaseAPIMixin, APITestCase):
    def get_case_serializer_clazz(self):
        return CaseSerializer

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
            "rejected",
            "date_of_birth",
            "category",
            "exempt_user",
            "exempt_user_reason",
            "ecf_statement",
            "case_count",
            "outcome_code",
            "outcome_description",
            "requires_action_at",
            "callback_time_string",
            "callback_attempt",
            "source",
            "complaint_flag",
            "eod_details",
            "call_started",
            "organisation_name",
            "organisation",
        ]


class CaseGeneralTestCase(BaseCaseTestCase, FullCaseAPIMixin):
    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # LIST
        self._test_delete_not_allowed(self.list_url)

        # DETAIL
        self._test_delete_not_allowed(self.detail_url)


class CreateCaseTestCase(BaseCaseTestCase):
    def test_create_doesnt_set_readonly_values_but_only_personal_details(self):
        """
        Only POST personal details allowed
        """
        pd = make_recipe("legalaid.personal_details")
        eligibility_check = make_recipe("legalaid.eligibility_check")
        thirdparty_details = make_recipe("legalaid.thirdparty_details")
        adaptation_details = make_recipe("legalaid.adaptation_details")
        diagnosis = make_recipe("diagnosis.diagnosis")
        provider = make_recipe("cla_provider.provider")
        organisation = make_recipe("call_centre.organisation")
        media_code = make_recipe("legalaid.media_code")

        matter_type1 = make_recipe("legalaid.matter_type1")
        matter_type2 = make_recipe("legalaid.matter_type2")

        data = {
            "personal_details": unicode(pd.reference),
            "eligibility_check": unicode(eligibility_check.reference),
            "thirdparty_details": unicode(thirdparty_details.reference),
            "adaptation_details": unicode(adaptation_details.reference),
            "diagnosis": unicode(diagnosis.reference),
            "provider": unicode(provider.id),
            "notes": "my notes",
            "billable_time": 234,
            "created": "2014-08-05T10:41:55.979Z",
            "modified": "2014-08-05T10:41:55.985Z",
            "created_by": "test_user",
            "matter_type1": matter_type1.code,
            "matter_type2": matter_type2.code,
            "media_code": media_code.code,
            "provider_notes": "bla",
            "source": CASE_SOURCE.VOICEMAIL,
            "laa_reference": 232323,
            "requires_action_by": REQUIRES_ACTION_BY.PROVIDER_REVIEW,
            "organisation": organisation.pk,
        }
        response = self.client.post(
            self.list_url, data=data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

        self.assertCaseEqual(
            response.data,
            Case(
                reference=response.data["reference"],
                personal_details=pd,
                eligibility_check=None,
                thirdparty_details=None,
                adaptation_details=None,
                diagnosis=None,
                provider=None,
                notes=data["notes"],
                billable_time=0,
                laa_reference=response.data["laa_reference"],
                matter_type1=matter_type1,
                matter_type2=matter_type2,
                media_code=media_code,
                source=CASE_SOURCE.VOICEMAIL,
                provider_notes="",
                organisation=None,
            ),
        )

        self.assertNotEqual(response.data["requires_action_by"], data["requires_action_by"])
        self.assertNotEqual(response.data["created"], data["created"])
        self.assertNotEqual(response.data["created_by"], data["created_by"])
        self.assertNotEqual(response.data["modified"], data["modified"])
        self.assertNotEqual(response.data["laa_reference"], data["laa_reference"])

        self.assertLogInDB()

    def test_create_no_data(self):
        """
        CREATE should work, even with an empty POST
        """
        response = self.client.post(self.list_url, data={}, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)
        self.assertEqual(response.data["eligibility_check"], None)
        self.assertEqual(response.data["source"], CASE_SOURCE.PHONE)

        # checking that requires_action_by is set to OPERATOR
        case = Case.objects.get(reference=response.data["reference"])
        self.assertEqual(case.requires_action_by, REQUIRES_ACTION_BY.OPERATOR)

        self.assertLogInDB()

    def test_create_with_data(self):
        media_code = make_recipe("legalaid.media_code")
        matter_type1 = make_recipe("legalaid.matter_type1")
        matter_type2 = make_recipe("legalaid.matter_type2")

        data = {
            "notes": "my notes",
            "matter_type1": matter_type1.code,
            "matter_type2": matter_type2.code,
            "media_code": media_code.code,
            "source": CASE_SOURCE.VOICEMAIL,
            "provider_notes": "bla",
        }
        response = self.client.post(
            self.list_url, data=data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

        self.assertCaseEqual(
            response.data,
            Case(
                reference=response.data["reference"],
                notes=data["notes"],
                matter_type1=matter_type1,
                matter_type2=matter_type2,
                media_code=media_code,
                source=CASE_SOURCE.VOICEMAIL,
                provider_notes="",
                laa_reference=response.data["laa_reference"],
            ),
        )

        self.assertLogInDB()

    def test_case_serializer_with_eligibility_check_reference(self):
        eligibility_check = make_recipe("legalaid.eligibility_check")

        data = {u"eligibility_check": eligibility_check.reference}
        serializer = CaseSerializer(data=data)
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

        serializer = CaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

    def test_case_serializer_with_media_code(self):
        media_code = make_recipe("legalaid.media_code")

        data = {u"media_code": media_code.code}
        serializer = CaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})


class UpdateCaseTestCase(BaseUpdateCaseTestCase, BaseCaseTestCase):
    @property
    def response_keys(self):
        return super(UpdateCaseTestCase, self).response_keys + ["complaint_count"]

    def test_patch_operator_notes_allowed(self):
        """
        Test that operator can post provider notes at max limit
        """
        self.assertEqual(CaseNotesHistory.objects.all().count(), 0)

        max_character_limit = "A" * CaseSerializer().fields["provider_notes"].max_length

        response = self.client.patch(
            self.detail_url,
            data={"notes": max_character_limit},
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["notes"], max_character_limit)

        self.assertEqual(CaseNotesHistory.objects.all().count(), 1)
        case_history = CaseNotesHistory.objects.last()
        self.assertEqual(case_history.operator_notes, max_character_limit)
        self.assertEqual(case_history.created_by, self.user)

    def test_patch_operator_notes_not_allowed_max_limit_hit(self):
        """
        Test that a bad request is made when user is over max character limit.
        """
        self.assertEqual(CaseNotesHistory.objects.all().count(), 0)

        over_max_character_limit = "A" * (CaseSerializer().fields["provider_notes"].max_length + 1)

        response = self.client.patch(
            self.detail_url,
            data={"notes": over_max_character_limit},
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data["notes"], over_max_character_limit)
        self.assertEqual(CaseNotesHistory.objects.all().count(), 0)

    def test_patch_provider_notes_not_allowed(self):
        """
        Test that provider cannot post provider notes
        """
        response = self.client.patch(
            self.detail_url,
            data={"provider_notes": "abc123"},
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider_notes"], self.resource.provider_notes)
        self.assertNotEqual(response.data["provider_notes"], "abc123")


class SuggestProviderTestCase(BaseCaseTestCase):
    #     # new tests to check assign_suggest view
    #     # this post always returns a response with the format:
    #     # {"suggested_provider": *, "as_of": "date_time",
    #     #  "suitable_providers":
    #     #  [{"name": "*", "id": pk, "short_code": "*",
    #     "telephone_frontdoor": "*", "telephone_backdoor": "0845 122 8677"},
    #     #  ...]}

    @classmethod
    def setUpTestData(cls):
        cls.suggested_cat_providers = None
        cls.suggested_category = None
        cls.cat_eligibility_check = None

    def setUp(self):
        super(CLAOperatorAuthBaseApiTestMixin, self).setUp()
        category1 = make_recipe("legalaid.category")
        category2 = make_recipe("legalaid.category")

        cat1_provider1 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=cat1_provider1, category=category1
        )

        cat1_provider2 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=cat1_provider2, category=category1
        )

        cat2_provider1 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=cat2_provider1, category=category2
        )
        cat2_provider2 = make_recipe("cla_provider.provider", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=cat2_provider2, category=category2
        )

        helper1 = ProviderAllocationHelper()
        self.suggested_cat_providers = helper1.get_qualifying_providers(category1)
        helper2 = ProviderAllocationHelper()
        self.other_cat_providers = helper2.get_qualifying_providers(category2)
        # create a case associated with the first category we created above
        self.suggested_category = category1
        self.cat_eligibility_check = make_recipe("legalaid.eligibility_check", category=self.suggested_category)

    @mock.patch("cla_provider.models.timezone.now")
    @mock.patch("cla_provider.helpers.timezone.now")
    def test_suggest_assign_case_without_category(self, tz_model_mock, tz_helper_tz):
        # should return null for suggested_provider and all providers as suitable
        case = make_recipe("legalaid.case", eligibility_check=None)
        return self._test_assign_suggest(case, tz_model_mock, tz_helper_tz, category_assigned=False, out_of_hours=True)

    @mock.patch("cla_provider.models.timezone.now")
    @mock.patch("cla_provider.helpers.timezone.now")
    def test_suggest_assign_case_with_category_out_of_hours(self, tz_model_mock, tz_helper_tz):
        # should return null for suggested_provider and providers within the same category as suitable
        case = make_recipe("legalaid.case", eligibility_check=self.cat_eligibility_check)
        category = case.eligibility_check.category
        self.assertEqual(category, self.suggested_category)
        return self._test_assign_suggest(case, tz_model_mock, tz_helper_tz, category_assigned=True, out_of_hours=True)

    @mock.patch("cla_provider.models.timezone.now")
    @mock.patch("cla_provider.helpers.timezone.now")
    def test_suggest_assign_case_with_category_in_hours(self, tz_model_mock, tz_helper_tz):
        # return named provider for suggested_provider and  providers with the same category as suitable
        case = make_recipe("legalaid.case", eligibility_check=self.cat_eligibility_check)
        category = case.eligibility_check.category
        self.assertEqual(category, self.suggested_category)
        return self._test_assign_suggest(case, tz_model_mock, tz_helper_tz, category_assigned=True, out_of_hours=False)

    def _test_assign_suggest(self, case, tz_model_mock, tz_helper_tz, category_assigned, out_of_hours):
        # fix the date and time so we can check in and out of hours.
        if out_of_hours:
            fake_day = datetime.datetime(2014, 1, 2, 22, 1, 0).replace(tzinfo=timezone.get_current_timezone())
        else:
            fake_day = datetime.datetime(2014, 1, 2, 9, 1, 0).replace(tzinfo=timezone.get_current_timezone())

        tz_model_mock.return_value = fake_day
        tz_helper_tz.return_value = fake_day

        url = reverse("call_centre:case-assign-suggest", args=(), kwargs={"reference": case.reference})
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check the suggested provider
        if out_of_hours or not category_assigned:
            self.assertIsNone(response.data["suggested_provider"])
        else:
            name = response.data["suggested_provider"]["name"]
            self.assertIn(name, [unicode(x.name) for x in self.suggested_cat_providers])
        #  now check the suitable_providers
        if category_assigned:
            # this should be all the providers in suggested category
            suitable_providers = [ProviderSerializer(p).data for p in self.suggested_cat_providers]
            self.assertEqual(response.data["suitable_providers"], suitable_providers)
        else:
            # this should be all providers
            suitable_providers = [
                ProviderSerializer(p).data for p in self.suggested_cat_providers + self.other_cat_providers
            ]
            self.assertEqual(response.data["suitable_providers"], suitable_providers)


class AssignCaseTestCase(BaseCaseTestCase):
    def test_assign_invalid_case_reference(self):
        url = reverse("call_centre:case-assign", args=(), kwargs={"reference": "invalid"})

        response = self.client.post(url, data={}, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(response.status_code, 404)

    @mock.patch("cla_provider.models.timezone.now")
    @mock.patch("cla_provider.helpers.timezone.now")
    def test_assign_case_without_category(self, tz_model_mock, tz_helper_tz):
        case = make_recipe("legalaid.case", eligibility_check=None)
        category = make_recipe("legalaid.category")
        return self._test_assign_successful(case, category, tz_model_mock, tz_helper_tz, is_manual=False)

    @mock.patch("cla_provider.models.timezone.now")
    @mock.patch("cla_provider.helpers.timezone.now")
    def test_manual_assign_successful(self, tz_model_mock, tz_helper_tz):
        case = make_recipe("legalaid.case")
        category = case.eligibility_check.category
        return self._test_assign_successful(case, category, tz_model_mock, tz_helper_tz, is_manual=True)

    @mock.patch("cla_provider.models.timezone.now")
    @mock.patch("cla_provider.helpers.timezone.now")
    def test_automatic_assign_successful(self, tz_model_mock, tz_helper_tz):
        case = make_recipe("legalaid.case")
        category = case.eligibility_check.category
        return self._test_assign_successful(case, category, tz_model_mock, tz_helper_tz, is_manual=False)

    def _test_assign_successful(self, case, category, tz_model_mock, tz_helper_tz, is_manual=True):
        fake_day = datetime.datetime(2014, 1, 2, 9, 1, 0).replace(tzinfo=timezone.get_current_timezone())
        tz_model_mock.return_value = fake_day
        tz_helper_tz.return_value = fake_day

        case.matter_type1 = make_recipe("legalaid.matter_type1", category=category)
        case.matter_type2 = make_recipe("legalaid.matter_type2", category=category)
        case.save()

        # preparing for test
        provider = make_recipe("cla_provider.provider", name="Provider Name", active=True)
        make_recipe(
            "cla_provider.provider_allocation", weighted_distribution=0.5, provider=provider, category=category
        )

        # before being assigned, case is in the list
        case_list = self.client.get(self.list_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token).data

        self.assertTrue(case.reference in [x.get("reference") for x in case_list["results"]])

        # no outcome codes should exist at this point
        self.assertEqual(Log.objects.count(), 0)

        # assign
        url = reverse("call_centre:case-assign", args=(), kwargs={"reference": case.reference})

        data = {"suggested_provider": provider.pk, "provider_id": provider.pk, "is_manual": is_manual}
        if is_manual:
            data["notes"] = "my notes"

        response = self.client.post(url, data=data, HTTP_AUTHORIZATION="Bearer %s" % self.token, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        case = Case.objects.get(pk=case.pk)
        self.assertIsNotNone(case.provider.pk)

        # after being assigned, it's gone from the dashboard...
        case_list = self.client.get(
            self.list_dashboard_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token
        ).data

        self.assertFalse(case.reference in [x.get("reference") for x in case_list["results"]])

        # checking that requires_action_by is set to PROVIDER
        self.assertEqual(case.requires_action_by, REQUIRES_ACTION_BY.PROVIDER_REVIEW)

        # checking that the log object is there
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]
        self.assertEqual(log.case, case)
        self.assertEqual(log.notes, "Assigned to Provider Name. %s" % data.get("notes", ""))
        self.assertEqual(log.created_by, self.user)

        # ... but the case still accessible from the full list
        case_list = self.client.get(self.list_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token).data

        self.assertTrue(case.reference in [x.get("reference") for x in case_list["results"]])

    def test_cannot_patch_provider_directly(self):
        """
        Need to use assign action instead
        """

        provider = make_recipe("cla_provider.provider", active=True)
        response = self.client.patch(
            self.detail_url, data={"provider": provider.pk}, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider"], None)


class DeferAssignmentTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse("call_centre:case-defer-assignment", args=(), kwargs={"reference": reference})


class DeclineHelpTestCase(ExplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_event_code(self):
        form = DeclineHelpCaseForm(case=mock.MagicMock())
        return form.fields["event_code"].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse("call_centre:case-decline-help", args=(), kwargs={"reference": reference})


class SuspendCaseTestCase(ExplicitEventCodeViewTestCaseMixin, MockGovNotifyMailBox, BaseCaseTestCase):
    def get_event_code(self):
        form = SuspendCaseForm(case=mock.MagicMock())
        return form.fields["event_code"].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse("call_centre:case-suspend", args=(), kwargs={"reference": reference})

    def get_event_code_data(self, code):
        return {"notes": "lorem ipsum", "event_code": code}

    def test_RDSP_fails_if_case_not_assigned(self):
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_event_code_data("RDSP")
        response = self.client.post(self.url, data=data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data, {"event_code": [u"You can only use RDSP if the case is assigned to a specialist"]}
        )
        self.assertEqual(Log.objects.count(), 0)

    def test_RDSP_successful(self):
        self.assertEquals(len(self.mailbox), 0)

        # assign case to provider
        provider = make_recipe("cla_provider.provider", active=True, email_address="example@example.com")
        self.resource.assign_to_provider(provider)

        # before, no logs
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_event_code_data("RDSP")
        response = self.client.post(self.url, data=data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)

        # after, log
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]

        self.assertEqual(log.case, self.resource)
        self.assertEqual(log.notes, self.get_expected_notes(data))
        self.assertEqual(log.created_by, self.user)

        self.assertEquals(len(self.mailbox), 1)

    def test_SAME_fails_if_case_hasnt_received_alternative_help(self):
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_event_code_data("SAME")
        response = self.client.post(self.url, data=data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data, {"event_code": [u"You can only use SAME if the client has received alternative help"]}
        )
        self.assertEqual(Log.objects.count(), 0)

    def test_SAME_successful(self):
        # creating COSPF code
        make_recipe("cla_eventlog.log", case=self.resource, code="COSPF")

        # before, no logs apart from the one just created
        self.assertEqual(Log.objects.count(), 1)

        data = self.get_event_code_data("SAME")
        response = self.client.post(self.url, data=data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)

        # after, log
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Log.objects.count(), 2)
        log = Log.objects.first()

        self.assertEqual(log.case, self.resource)
        self.assertEqual(log.notes, self.get_expected_notes(data))
        self.assertEqual(log.created_by, self.user)


class SearchCaseTestCase(BaseSearchCaseAPIMixin, BaseCaseTestCase):
    def test_list_with_dashboard_param(self):
        """
        Testing that if ?dashboard param is specified, it will exclude cases
        that are already assigned or don't requires_action_by == OPERATOR
        """
        Case.objects.all().delete()

        now = timezone.now()
        # ref1 is assigned => EXCLUDED
        # ref2.requires_action_by == None (meaning doesn't require action) => EXCLUDED
        # ref3.requires_action_by == OPERATOR => INCLUDED
        # ref4.requires_action_at > now => EXCLUDED
        # ref5.requires_action_at < now => INCLUDED
        # ref6.requires_action_at < now => INCLUDED
        # ref7.requires_action_at < now => INCLUDED
        make_recipe(
            "legalaid.case",
            reference="ref1",
            provider=self.provider,
            outcome_code="REF-EXT",
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
        )
        make_recipe("legalaid.case", reference="ref2", provider=None, outcome_code="MIS", requires_action_by=None)
        make_recipe(
            "legalaid.case",
            reference="ref3",
            provider=None,
            outcome_code="COI",
            requires_action_by=REQUIRES_ACTION_BY.OPERATOR,
        )
        make_recipe(
            "legalaid.case",
            reference="ref4",
            provider=None,
            requires_action_by=REQUIRES_ACTION_BY.OPERATOR,
            outcome_code="CB1",
            requires_action_at=now + datetime.timedelta(seconds=2),
        )
        make_recipe(
            "legalaid.case",
            reference="ref5",
            provider=None,
            requires_action_by=REQUIRES_ACTION_BY.OPERATOR,
            outcome_code="CB1",
            requires_action_at=now - datetime.timedelta(seconds=1),
        )
        make_recipe(
            "legalaid.case",
            reference="ref6",
            provider=None,
            requires_action_by=REQUIRES_ACTION_BY.OPERATOR,
            outcome_code="CB1",
            requires_action_at=now - datetime.timedelta(days=1),
        )
        make_recipe(
            "legalaid.case",
            reference="ref7",
            provider=None,
            requires_action_by=REQUIRES_ACTION_BY.OPERATOR,
            outcome_code="CB2",
            requires_action_at=now - datetime.timedelta(days=2),
        )

        # searching via dashboard param => should return ref3, ref4, ref5
        response = self.client.get(self.list_dashboard_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, len(response.data["results"]))
        self.assertEqual([case["reference"] for case in response.data["results"]], ["ref3", "ref6", "ref5", "ref7"])

        # searching without dashboard param => should return all of them
        response = self.client.get(self.list_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(7, len(response.data["results"]))
        self.assertEqual(
            [case["reference"] for case in response.data["results"]],
            ["ref1", "ref2", "ref3", "ref6", "ref5", "ref4", "ref7"],
        )

    # person_ref PARAM

    def test_list_with_person_ref_param(self):
        """
        Testing that if ?person_ref param is specified, it will only return
        cases for that person
        """
        Case.objects.all().delete()

        pd1 = make_recipe("legalaid.personal_details")
        pd2 = make_recipe("legalaid.personal_details")

        make_recipe("legalaid.case", reference="ref1", personal_details=pd1)
        make_recipe("legalaid.case", reference="ref2", personal_details=pd2)
        make_recipe("legalaid.case", reference="ref3", personal_details=pd1)

        # searching for pd1
        response = self.client.get(
            self.get_list_person_ref_url(pd1.reference),
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data["results"]))
        self.assertItemsEqual([c["reference"] for c in response.data["results"]], ["ref1", "ref3"])

        # searching for pd2 AND dashboard=1 should ignore dashboard param
        url = "%s&dashboard=1" % self.get_list_person_ref_url(pd2.reference)
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data["results"]))
        self.assertItemsEqual([case["reference"] for case in response.data["results"]], ["ref2"])


class FilteredSearchCaseTestCase(BaseCaseTestCase):
    def setUp(self):
        """
        obj1 created by current operator (phone implicit)
        obj2 created by another operator (phone implicit)
        obj3 case by phone (explicit)
        obj4 case from web (explicit)
        obj5 case with EOD (web explicit)
        """
        super(FilteredSearchCaseTestCase, self).setUp()

        Case.objects.all().delete()

        # operator1 = make_recipe('call_centre.operator')
        # operator2 = make_recipe('call_centre.operator')

        self.cases = [
            # obj1 created by current operator (phone implicit)
            make_recipe("legalaid.case", reference="ref1", created_by=self.operator.user),
            # obj2 created by another operator (phone implicit)
            make_recipe("legalaid.case", reference="ref2", created_by=self.operator_manager.user),
            # obj3 case by phone
            make_recipe("legalaid.case", reference="ref3", created_by=self.operator.user, source=CASE_SOURCE.PHONE),
            # obj4 case from web
            make_recipe("legalaid.case", reference="ref4", created_by=self.operator.user, source=CASE_SOURCE.WEB),
            # obj5 case with EOD (from web)
            make_recipe("legalaid.case", reference="ref5", created_by=self.operator.user, source=CASE_SOURCE.WEB),
        ]
        make_recipe("legalaid.eod_details", notes="hello", case=self.cases[-1])

    def getAndAssertValidResponse(self, filter_name, expected):
        response = self.client.get(
            u"%s?only=%s" % (self.list_url, filter_name),
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(expected), response.data["count"])
        self.assertItemsEqual([c["reference"] for c in response.data["results"]], expected)

    def test_all_cases(self):
        self.getAndAssertValidResponse("", ["ref1", "ref2", "ref3", "ref4", "ref5"])

    def test_phone_cases(self):
        self.getAndAssertValidResponse("phone", ["ref1", "ref2", "ref3"])

    def test_web_cases(self):
        self.getAndAssertValidResponse("web", ["ref4", "ref5"])

    def test_operator_cases(self):
        self.getAndAssertValidResponse("my", ["ref1", "ref3", "ref4", "ref5"])

    def test_eod_cases(self):
        self.getAndAssertValidResponse("eod", ["ref5"])


class FutureCallbacksCaseTestCase(BaseCaseTestCase):
    def test_get_list(self):
        Case.objects.all().delete()

        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # ref1.requires_action_at == past => EXCLUDED
        # ref2.requires_action_at == None => EXCLUDED
        # ref3.requires_action_at == start_of_day+7 => INCLUDED
        # ref4.requires_action_at > start_of_day+7 => EXCLUDED
        # ref5.requires_action_at == start_of_day => INCLUDED
        make_recipe("legalaid.case", reference="ref1", requires_action_at=start_of_day - datetime.timedelta(seconds=1))
        make_recipe("legalaid.case", reference="ref2", requires_action_at=None)
        make_recipe(
            "legalaid.case",
            reference="ref3",
            requires_action_at=start_of_day + datetime.timedelta(days=7) - datetime.timedelta(seconds=1),
        )
        make_recipe("legalaid.case", reference="ref4", requires_action_at=start_of_day + datetime.timedelta(days=7))
        make_recipe("legalaid.case", reference="ref5", requires_action_at=start_of_day)

        # searching
        url = reverse("call_centre:case-future-callbacks")
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        self.assertItemsEqual([case["reference"] for case in response.data], ["ref5", "ref3"])


class SearchForPersonalDetailsTestCase(BaseCaseTestCase):
    def make_resource(self, **kwargs):
        """
            Specifying case.personal_details == None by default
        """
        kwargs["personal_details"] = None
        return super(SearchForPersonalDetailsTestCase, self).make_resource(**kwargs)

    def setUp(self):
        super(SearchForPersonalDetailsTestCase, self).setUp()

        def make_pd(full_name, postcode=None, dob=None, vulnerable=False):
            return make_recipe(
                "legalaid.personal_details",
                full_name=full_name,
                postcode=postcode,
                date_of_birth=dob,
                vulnerable_user=vulnerable,
            )

        # creating personal details objects
        self.pds = [
            make_pd("John Doe", "SW1H 9AJ", timezone.now(), False),
            make_pd("John Smith", None, None, False),
            make_pd("Ethan Engelking", None, None, False),
            make_pd("John Smith2", None, None, True),
        ]

    def get_search_for_pd_url(self, person_q, case_reference=None):
        case_reference = case_reference or self.resource.reference
        return u"%s?person_q=%s" % (
            reverse("call_centre:case-search-for-personal-details", args=(), kwargs={"reference": case_reference}),
            person_q,
        )

    def test_404(self):
        url = self.get_search_for_pd_url("", case_reference="invalid")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_400_with_case_with_pd_already_attached(self):
        self.resource.personal_details = self.pds[0]
        self.resource.save()

        url = self.get_search_for_pd_url("")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_empty_with_empty_param(self):
        url = self.get_search_for_pd_url("")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_returns_empty_with_param_len_lt_3(self):
        url = self.get_search_for_pd_url("jo")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_returns_list_with_param_len_gte_3(self):
        # should only return reference, full_name, dob and postcode
        url = self.get_search_for_pd_url("joh")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertItemsEqual(response.data[0].keys(), ["reference", "full_name", "postcode", "dob"])
        self.assertItemsEqual(
            [(p["full_name"], p["postcode"]) for p in response.data], [("John Doe", "SW1H 9AJ"), ("John Smith", None)]
        )

    def test_doesnt_return_vulnerable_users(self):
        url = self.get_search_for_pd_url("John Smith2")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class LinkPersonalDetailsTestCase(BaseCaseTestCase):
    def make_resource(self, **kwargs):
        """
        Specifying case.personal_details == None by default
        """
        kwargs["personal_details"] = None
        return super(LinkPersonalDetailsTestCase, self).make_resource(**kwargs)

    def setUp(self):
        super(LinkPersonalDetailsTestCase, self).setUp()
        self.pd = make_recipe("legalaid.personal_details")

    def get_link_to_pd_url(self, case_reference=None):
        case_reference = case_reference or self.resource.reference
        return reverse("call_centre:case-link-personal-details", args=(), kwargs={"reference": case_reference})

    def test_404(self):
        url = self.get_link_to_pd_url(case_reference="invalid")
        response = self.client.post(url, data={}, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_400_with_case_with_pd_already_attached(self):
        self.resource.personal_details = self.pd
        self.resource.save()

        url = self.get_link_to_pd_url()
        response = self.client.post(
            url, data={"personal_details": "abcd"}, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {"error": "A person is already linked to this case"})

    def test_returns_400_if_data_not_passed(self):
        url = self.get_link_to_pd_url()
        response = self.client.post(url, data={}, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {"error": 'Param "personal_details" required'})

    def test_returns_400_if_pd_obj_not_found(self):
        url = self.get_link_to_pd_url()
        response = self.client.post(
            url, data={"personal_details": "abcd"}, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {"error": 'Person with reference "abcd" not found'})

    def test_link_to_pd_successful(self):
        self.assertEqual(self.resource.personal_details, None)

        url = self.get_link_to_pd_url()
        response = self.client.post(
            url, data={"personal_details": self.pd.reference}, HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.resource = self.resource.__class__.objects.get(pk=self.resource.pk)
        self.assertEqual(self.resource.personal_details, self.pd)


class CallMeBackTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse("call_centre:case-call-me-back", args=(), kwargs={"reference": reference})

    @mock.patch("call_centre.forms.timezone.now")
    def __call__(self, runner, mocked_now, *args, **kwargs):
        self.mocked_now = mocked_now
        self.mocked_now.return_value = datetime.datetime(2015, 3, 23, 10, 0, 0, 0).replace(tzinfo=timezone.utc)

        super(CallMeBackTestCase, self).__call__(runner, *args, **kwargs)

    @property
    def _default_dt(self):
        if not hasattr(self, "__default_dt"):
            self.__default_dt = self.mocked_now()
            self.__default_dt = self.__default_dt.replace(hour=11)
        return self.__default_dt

    @property
    def _default_local_dt(self):
        return timezone.localtime(self._default_dt)

    @property
    def _default_local_dt_sla_15(self):
        return self._default_local_dt + datetime.timedelta(minutes=15)

    @property
    def _default_local_dt_sla_30(self):
        return self._default_local_dt + datetime.timedelta(minutes=30)

    @property
    def _default_local_dt_sla_120(self):
        return self._default_local_dt + datetime.timedelta(minutes=120)

    @property
    def _default_local_dt_sla_480(self):
        return self._default_local_dt + datetime.timedelta(hours=8)

    def get_expected_notes(self, data):
        return "Callback scheduled for %s - %s. %s" % (
            timezone.localtime(self._default_dt).strftime("%d/%m/%Y %H:%M"),
            (timezone.localtime(self._default_dt) + datetime.timedelta(minutes=30)).strftime("%H:%M"),
            data["notes"],
        )

    def get_default_post_data(self):
        return {"notes": "lorem ipsum", "datetime": self._default_dt.strftime("%Y-%m-%d %H:%M")}

    def _test_cbx(self, cb_no):
        self.resource.callback_attempt = cb_no - 1
        self.resource.save()

        with mock.patch(
            "cla_common.call_centre_availability.current_datetime",
            return_value=datetime.datetime(2015, 3, 23, 10, 0, 0, 0),
        ):
            self.test_successful()

        log = self.resource.log_set.first()
        self.assertEqual(log.code, "CB{}".format(cb_no))
        self.maxDiff = None
        self.assertEqual(parse(log.context["requires_action_at"]), self._default_dt)
        self.assertEqual(parse(log.context["sla_120"]), self._default_local_dt_sla_120)
        self.assertEqual(parse(log.context["sla_480"]), self._default_local_dt_sla_480)
        self.assertEqual(parse(log.context["sla_15"]), self._default_local_dt_sla_15)
        self.assertEqual(parse(log.context["sla_30"]), self._default_local_dt_sla_30)

    def test_successful_CB1(self):
        self._test_cbx(1)

    def test_successful_CB2(self):
        self._test_cbx(2)

    def test_successful_CB3(self):
        self._test_cbx(3)


class StopCallMeBackTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def make_resource(self, **kwargs):
        kwargs["callback_attempt"] = 1
        return super(StopCallMeBackTestCase, self).make_resource(**kwargs)

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse("call_centre:case-stop-call-me-back", args=(), kwargs={"reference": reference})

    def get_default_post_data(self):
        return {"notes": "lorem ipsum", "action": "complete"}

    def test_successful_CALLBACK_COMPLETE(self):
        self.resource.callback_attempt = 1
        self.resource.save()

        self._test_successful(data={"notes": "lorem ipsum", "action": "complete"})

        log = self.resource.log_set.first()
        self.assertEqual(log.code, "CALLBACK_COMPLETE")

    def test_successful_CBC(self):
        self.resource.callback_attempt = 1
        self.resource.save()

        self._test_successful(data={"notes": "lorem ipsum", "action": "cancel"})

        log = self.resource.log_set.first()
        self.assertEqual(log.code, "CBC")
