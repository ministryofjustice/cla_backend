from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.tests.views.mixins.case_api import FullCaseAPIMixin
from legalaid.models import Case
from cla_eventlog.models import Log
from cla_eventlog.constants import LOG_LEVELS, LOG_TYPES
from core.tests.mommy_utils import make_recipe
from complaints.models import Complaint
from .test_case_api import BaseCaseTestCase


class OrganisationComplaintsTestCase(BaseCaseTestCase, FullCaseAPIMixin):
    def setUp(self):
        super(OrganisationComplaintsTestCase, self).setUp()

        self.foo_org = make_recipe("call_centre.organisation", name="Organisation Foo")
        self.foo_org_operator = make_recipe(
            "call_centre.operator", is_manager=False, is_cla_superuser=False, organisation=self.foo_org
        )

        self.bar_org = make_recipe("call_centre.organisation", name="Organisation Bar")
        self.bar_org_operator = make_recipe(
            "call_centre.operator", is_manager=False, is_cla_superuser=False, organisation=self.bar_org
        )

        self.no_org_operator = make_recipe("call_centre.operator", is_manager=False, is_cla_superuser=False)

    def test_operator_create_complaint_against_case_with_organisation(self):
        # Only operators of the same organisation as the operator that created
        # the case can register an Complaint against the case

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)
        eod = make_recipe("legalaid.eod_details", case=case)
        data = {"eod": str(eod.reference), "description": "This is a description"}

        url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)
        # (organisation, can_create)
        organisations = [(self.foo_org, True), (self.bar_org, False), (None, False)]
        for organisation, can_create in organisations:
            self.operator.organisation = organisation
            self.operator.save()

            response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            expected_status_code = status.HTTP_201_CREATED if can_create else status.HTTP_403_FORBIDDEN
            self.assertEqual(expected_status_code, response.status_code)

    def test_any_operator_can_create_complaint_against_case_without_organisation(self):
        # Any operator can register an Complaint against a case when the case creator does not belong to an organisation

        case = make_recipe("legalaid.case", created_by=self.no_org_operator.user)
        eod = make_recipe("legalaid.eod_details", case=case)
        data = {"eod": str(eod.reference), "description": "This is a description"}

        url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)

        # (organisation, can_create)
        organisations = [(self.foo_org, True), (self.bar_org, True), (None, True)]
        for organisation, can_create in organisations:
            self.operator.organisation = organisation
            self.operator.save()

            response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            expected_status_code = status.HTTP_201_CREATED if can_create else status.HTTP_403_FORBIDDEN
            self.assertEqual(expected_status_code, response.status_code)

    def test_case_without_organisation_is_reassigned_on_complaint_details_creation(self):
        # Cases created by operators with no organisation are reassigned to current
        # operator when registering an complaint against a case

        case = make_recipe("legalaid.case", created_by=self.no_org_operator.user)
        eod = make_recipe("legalaid.eod_details", case=case)
        data = {"eod": str(eod.reference), "description": "This is a description"}
        url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)
        self.assertEqual(self.no_org_operator.user.id, case.created_by.id)

        self.operator.organisation = self.foo_org
        self.operator.save()
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        case_reloaded = Case.objects.get(pk=case.id)
        self.assertEqual(self.operator.user.id, case_reloaded.created_by.id)
        self.assertIn(("CASE_CREATED_BY_CHANGED",), Log.objects.filter(case_id=case.id).values_list("code"))

        self.operator_manager.organisation = self.bar_org
        self.operator_manager.save()
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_all_operator_managers_can_see_complaints_count(self):
        # All Operator managers should be able to see that there is a Complaint against
        # Even if the case creator belongs to another organisation.

        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        complaints = make_recipe(
            "complaints.complaint", eod=eod, description="This is a test", category=None, _quantity=3
        )

        # (organisation, eod_details_editable)
        organisations = [(self.foo_org, False), (self.bar_org, True), (None, False)]
        for organisation, eod_details_editable in organisations:
            self.operator_manager.organisation = organisation
            self.operator_manager.save()

            url = reverse(u"%s:case-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})
            response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
            self.assertEqual(response.data.get("complaint_count"), len(complaints))
            self.assertEqual(response.data.get("eod_details_editable"), eod_details_editable)

    def test_all_operator_managers_can_see_all_complaints_in_dashboard(self):
        # All Operator Managers should be able to see that there is a complaint against a case in the Complaints tab.
        # Even if the complaint belongs to another organisation.

        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        complaints = make_recipe(
            "complaints.complaint", eod=eod, description="This is a test", category=None, _quantity=3
        )

        # (organisation, is_editable)
        organisations = [(self.foo_org, False), (self.bar_org, True), (None, False)]
        for organisation, is_editable in organisations:
            self.operator_manager.organisation = organisation
            self.operator_manager.save()
            self._assert_complaint_dashboard(complaints, is_editable=is_editable)

    def test_cla_superuser_can_update_all_complaints(self):
        self.operator_manager.organisation = None
        self.operator_manager.is_cla_superuser = True
        self.operator_manager.save()

        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        complaints = make_recipe(
            "complaints.complaint", eod=eod, description="This is a test", category=None, _quantity=3
        )
        self._assert_complaint_dashboard(complaints, is_editable=True)

    def test_operator_with_organisation_can_see_complaints_created_activity_in_log(self):
        # Case activity log should contain COMPLAINT_CREATED records created by same organisation

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)
        log = make_recipe(
            "cla_eventlog.log",
            case=case,
            level=LOG_LEVELS.HIGH,
            type=LOG_TYPES.SYSTEM,
            code="COMPLAINT_CREATED",
            created_by=self.foo_org_operator.user,
            notes="This is a test",
        )

        # (organisation, can_see_complaint_log)
        organisations = [(self.foo_org, True), (self.bar_org, False), (None, False)]
        url = reverse(u"%s:log-list" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference})
        for organisation, can_view in organisations:
            self.operator.organisation = organisation
            self.operator.save()
            response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            if can_view:
                self.assertEqual(len(response.data), 1)
                self.assertEqual(response.data[0].get("code"), log.code)
                self.assertEqual(response.data[0].get("notes"), log.notes)
            else:
                self.assertEqual(len(response.data), 0)

    def test_cla_superuser_can_see_all_complaints_created_in_activity_log(self):
        self.operator.is_cla_superuser = True
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)
        log = make_recipe(
            "cla_eventlog.log",
            case=case,
            level=LOG_LEVELS.HIGH,
            type=LOG_TYPES.SYSTEM,
            code="COMPLAINT_CREATED",
            created_by=self.foo_org_operator.user,
            notes="This is a test",
        )

        url = reverse(u"%s:log-list" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference})
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("code"), log.code)
        self.assertEqual(response.data[0].get("notes"), log.notes)

    def _assert_complaint_dashboard(self, complaints, is_editable):
        complaint_ids = [complaint.id for complaint in complaints]
        url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(response.data.get("count"), Complaint.objects.all().count())
        results = response.data.get("results")
        for complaint in results:
            self.assertIn(complaint.get("id"), complaint_ids)
            self.assertEqual(complaint.get("is_editable"), is_editable)
