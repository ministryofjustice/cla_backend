from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.tests.views.mixins.case_api import FullCaseAPIMixin
from core.tests.mommy_utils import make_recipe
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
    """

    def test_operator_manager_case_creator_different_organisation_see_complaints_count(self):
        self.operator_manager.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        complaints = make_recipe(
            "complaints.complaint", eod=eod, description="This is a test", category=None, _quantity=3
        )

        url = reverse(u"%s:case-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(response.data.get("complaint_count"), len(complaints))
        return response

    """
    All Operator Managers should be able to see that there is a complaint against
    """

    def test_operator_manager_case_creator_same_organisation_see_complaints_count(self):
        self.operator_manager.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        complaints = make_recipe(
            "complaints.complaint", eod=eod, description="This is a test", category=None, _quantity=3
        )

        url = reverse(u"%s:case-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})
        response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(response.data.get("complaint_count"), len(complaints))
        return response
