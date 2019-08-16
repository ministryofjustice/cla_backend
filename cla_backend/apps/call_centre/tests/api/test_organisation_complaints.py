from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.tests.views.mixins.case_api import FullCaseAPIMixin
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

    """
    When an a case is created by an operator that has a organisation then only operators of the same organisation
    can register complaints against that case.
    """

    def test_operator_can_create_complaint_for_cases_created_by_operator_of_same_organisation(self):
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)
        eod = make_recipe("legalaid.eod_details", case=case)

        create_complaint_url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)

        data = {"eod": str(eod.reference), "description": "This is a description"}
        response = self.client.post(
            create_complaint_url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    """
    When an a case is created by an operator that has a organisation then only operators of the same organisation
    can register complaints against that case.
    """

    def test_operator_cannot_create_complaint_for_cases_created_by_operator_of_another_organisation(self):
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", case=case)

        create_complaint_url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)

        data = {"eod": str(eod.reference), "description": "This is a description"}
        response = self.client.post(
            create_complaint_url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    """
    When a case is created by an user that does not have a organisation then any operator or
    operator manager can register a complaint against that case.
    """

    def test_operator_can_create_complaint_for_cases_created_by_operator_with_no_organisation(self):
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.no_org_operator.user)
        eod = make_recipe("legalaid.eod_details", case=case)

        create_complaint_url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)

        data = {"eod": str(eod.reference), "description": "This is a description"}

        response = self.client.post(
            create_complaint_url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    """
    All Operator Managers should be able to see that there is a complaint against
    Even if the case creator belongs to another organisation.
    """

    def test_operator_manager_see_complaints_count(self):
        self.operator_manager.organisation = self.foo_org
        self.operator_manager.save()

        # Case creator belongs to another organisation
        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        complaints = make_recipe(
            "complaints.complaint", eod=eod, description="This is a test", category=None, _quantity=3
        )

        url = reverse(u"%s:case-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(response.data.get("complaint_count"), len(complaints))
        self.assertFalse(response.data.get("eod_details_editable"))

        # Case creator doesn't have organisation
        self.operator_manager.organisation = None
        self.operator_manager.save()

        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(response.data.get("complaint_count"), len(complaints))
        self.assertTrue(response.data.get("eod_details_editable"))

        # Case creator belongs to same organisation
        self.operator_manager.organisation = self.bar_org
        self.operator_manager.save()

        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(response.data.get("complaint_count"), len(complaints))
        self.assertTrue(response.data.get("eod_details_editable"))

    """
    All Operator Managers should be able to see that there is a complaint against a case in the Complaints tab.
    Even if the complaint belongs to another organisation.
    """

    def test_operator_manager_can_see_all_complaints_in_dashboard(self):
        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        complaints = make_recipe(
            "complaints.complaint", eod=eod, description="This is a test", category=None, _quantity=3
        )

        # Case creator belongs to another organisation
        self.operator_manager.organisation = self.foo_org
        self.operator_manager.save()
        self._assert_complaint_dashboard(complaints, complaint_editable=False)

        # Case creator doesn't have organisation
        self.operator_manager.organisation = None
        self.operator_manager.save()
        self._assert_complaint_dashboard(complaints, complaint_editable=True)

        # Case creator belongs to same organisation
        self.operator_manager.organisation = self.bar_org
        self.operator_manager.save()
        self._assert_complaint_dashboard(complaints, complaint_editable=True)

    def _assert_complaint_dashboard(self, complaints, complaint_editable):
        complaint_ids = [complaint.id for complaint in complaints]
        url = reverse(u"%s:complaints-list" % self.API_URL_NAMESPACE)
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(response.data.get("count"), Complaint.objects.all().count())
        results = response.data.get("results")
        for complaint in results:
            self.assertIn(complaint.get("id"), complaint_ids)
            self.assertEqual(complaint.get("complaint_editable"), complaint_editable)
