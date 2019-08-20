from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.tests.views.mixins.case_api import FullCaseAPIMixin
from legalaid.models import Case
from cla_eventlog.models import Log
from cla_common.constants import EXPRESSIONS_OF_DISSATISFACTION
from core.tests.mommy_utils import make_recipe
from .test_case_api import BaseCaseTestCase


class OrganisationCaseAssignmentTestCase(BaseCaseTestCase, FullCaseAPIMixin):
    def setUp(self):
        super(OrganisationCaseAssignmentTestCase, self).setUp()
        self.foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")
        self.bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")

    def test_case_organisation_is_set_when_operator_create_case(self):
        # Assign operator organisation as the case organisation when a case is created

        organisations = [self.foo_org, self.bar_org, None]
        url = reverse(u"%s:case-list" % self.API_URL_NAMESPACE)
        for organisation in organisations:
            self.operator.organisation = organisation
            self.operator.save()
            case = make_recipe("legalaid.case", organisation=organisation)
            response = self.client.post(url, data={}, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(status.HTTP_201_CREATED, response.status_code)
            self._assert_case_organisation_updated(case, organisation, response, check_status_log=False)
            self.assertNotIn(("CASE_ORGANISATION_SET",), Log.objects.filter(case_id=case.id).values_list("code"))

    def test_case_organisation_is_set_when_operator_updates_case_without_organisation(self):
        # Assign operator organisation as the case organisation when
        # a case without organisation is updated

        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", organisation=None)
        self.assertIsNone(case.organisation)

        url = reverse(u"%s:case-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})
        data = {"notes": "This is a test", "provider_notes": ""}
        response = self.client.patch(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self._assert_case_organisation_updated(case, self.foo_org, response)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_case_organisation_is_set_when_operator_suspends_case_without_organisation(self):
        # Assign operator organisation as the case organisation when
        # a case without organisation gets suspended
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", organisation=None)
        self.assertIsNone(case.organisation)

        url = reverse(u"%s:case-suspend" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})
        data = {"notes": "", "event_code": "INSUF"}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self._assert_case_organisation_updated(case, self.foo_org, response)

    def test_case_organisation_is_set_when_operator_assigns_alternative_help_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when
        # a case without organisation gets assigned alternative help
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", organisation=None)
        article = make_recipe("knowledgebase.article", service_name="TEST SERVICE")
        self.assertIsNone(case.organisation)

        url = reverse(
            u"%s:case-assign-alternative-help" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference}
        )
        data = {"notes": "", "event_code": "IRKB", "selected_providers": [article.id]}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self._assert_case_organisation_updated(case, self.foo_org, response)

    def test_case_organisation_is_set_when_operator_decline_help_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when
        # a case without organisation gets declined help
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", organisation=None)
        self.assertIsNone(case.organisation)

        url = reverse(u"%s:case-decline-help" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})
        data = {"notes": "", "event_code": "DECL"}
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self._assert_case_organisation_updated(case, self.foo_org, response)

    def test_case_organisation_is_set_when_operator_adds_eod_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when a eod is
        # added to a case without organisation no organisation

        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", organisation=None)
        self.assertIsNone(case.organisation)

        url = reverse(
            u"%s:eoddetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        data = {
            "case_reference": case.reference,
            "categories": [{"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False}],
            "notes": "",
        }

        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self._assert_case_organisation_updated(case, self.foo_org, response)

        # Organisation should not change when another operator adds an eod
        self.operator_manager.organisation = self.bar_org
        self.operator_manager.save()

        data["reference"] = response.data.get("reference")
        del data["case_reference"]
        response = self.client.patch(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self._assert_case_organisation_updated(case, self.foo_org, response, check_status_log=False)

    def test_case_organisation_is_set_when_operator_adds_complaint_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when a complaint is
        # added to a case without organisation no organisation
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", organisation=None)
        eod = make_recipe("legalaid.eod_details", case=case)
        self.assertIsNone(case.organisation)

        data = {"eod": str(eod.reference), "description": "This is a description"}
        url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self._assert_case_organisation_updated(case, self.foo_org, response)

        # Organisation should not change when another operator adds a complaint
        self.operator_manager.organisation = self.bar_org
        self.operator_manager.save()

        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self._assert_case_organisation_updated(case, self.foo_org, response, check_status_log=False)

    def test_case_organisation_is_set_when_operator_adds_adaptation_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when a adaptation is
        # added to a case without organisation no organisation
        case = make_recipe("legalaid.case", organisation=None)
        data = {
            "bsl_webcam": True,
            "minicom": True,
            "text_relay": True,
            "skype_webcam": True,
            "language": "ENGLISH",
            "notes": "my notes",
            "callback_preference": True,
            "case_reference": case.reference,
        }

        self.operator.organisation = self.foo_org
        self.operator.save()

        url = reverse(
            u"%s:adaptationdetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self._assert_case_organisation_updated(case, self.foo_org, response)

    def test_case_organisation_is_set_when_operator_adds_personal_detail_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when a personal detail is
        # added to a case without organisation no organisation
        case = make_recipe("legalaid.case", organisation=None, personal_details=None)
        data = {"full_name": "John Smith", "case_reference": case.reference}

        self.operator.organisation = self.foo_org
        self.operator.save()

        url = reverse(
            u"%s:personaldetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self._assert_case_organisation_updated(case, self.foo_org, response)

    def test_case_organisation_is_set_when_operator_adds_third_party_detail_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when a third party detail is
        # added to a case without organisation no organisation

        case = make_recipe("legalaid.case", organisation=None, personal_details=None)
        data = {
            "personal_details": {"full_name": "John Smith"},
            "case_reference": case.reference,
            "personal_relationship": "PROFESSIONAL",
            "pass_phrase": "pass",
        }

        self.operator.organisation = self.foo_org
        self.operator.save()

        url = reverse(
            u"%s:thirdpartydetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self._assert_case_organisation_updated(case, self.foo_org, response)

    def test_case_organisation_is_set_when_operator_adds_diagnosis_to_case_without_organisation(self):
        # Assign operator organisation as the case organisation when a diagnosis is
        # added to a case without organisation no organisation

        case = make_recipe("legalaid.case", organisation=None, personal_details=None)
        data = {}

        self.operator.organisation = self.foo_org
        self.operator.save()

        url = reverse(
            u"%s:diagnosis-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self._assert_case_organisation_updated(case, self.foo_org, response)

    def _assert_case_organisation_updated(self, case, expected_organisation, response=None, check_status_log=True):
        case_reloaded = Case.objects.get(pk=case.id)
        self.assertEqual(case_reloaded.organisation, expected_organisation)
        if check_status_log:
            self.assertIn(("CASE_ORGANISATION_SET",), Log.objects.filter(case_id=case.id).values_list("code"))
