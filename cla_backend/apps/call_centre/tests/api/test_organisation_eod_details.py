import json

from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.models import EODDetails
from legalaid.tests.views.mixins.case_api import FullCaseAPIMixin
from cla_common.constants import EXPRESSIONS_OF_DISSATISFACTION
from core.tests.mommy_utils import make_recipe
from .test_case_api import BaseCaseTestCase


class OrganisationEODDetailsTestCase(BaseCaseTestCase, FullCaseAPIMixin):
    def setUp(self):
        super(OrganisationEODDetailsTestCase, self).setUp()

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
    can register complaints and EOD against that case.
    """

    def test_operator_can_create_eod_for_cases_created_by_operator_of_same_organisation(self):
        from cla_common.constants import EXPRESSIONS_OF_DISSATISFACTION

        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)

        path = u"%s:eoddetails-detail" % self.API_URL_NAMESPACE
        create_eod_url = reverse(path, args=(), kwargs={"case_reference": case.reference})

        data = {
            "case_reference": case.reference,
            "categories": [{"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False}],
            "notes": "",
        }
        response = self.client.post(create_eod_url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        return response

    def test_operator_can_update_eod_for_cases_created_by_operator_of_same_organisation(self):
        from cla_common.constants import EXPRESSIONS_OF_DISSATISFACTION

        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        self.assertEqual(eod.categories.count(), 0)

        path = u"%s:eoddetails-detail" % self.API_URL_NAMESPACE
        create_eod_url = reverse(path, args=(), kwargs={"case_reference": case.reference})

        data = {
            "reference": str(eod.reference),
            "categories": [
                {"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False},
                {"category": EXPRESSIONS_OF_DISSATISFACTION.PASS_TO_PUBLIC, "is_major": False},
            ],
            "notes": "",
        }
        response = self.client.patch(create_eod_url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        eod_reloaded = EODDetails.objects.get(reference=eod.reference)
        self.assertEqual(eod_reloaded.categories.count(), 2)
        return response

    """
    When an a case is created by an operator that has a organisation then only operators of the same organisation
    can register complaints and EOD against that case.
    """

    def test_operator_cannot_create_eod_for_cases_created_by_operator_of_another_organisation(self):
        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        path = u"%s:eoddetails-detail" % self.API_URL_NAMESPACE
        create_eod_url = reverse(path, args=(), kwargs={"case_reference": case.reference})
        data = {
            "case_reference": case.reference,
            "categories": [{"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False}],
            "notes": "",
        }
        response = self.client.post(create_eod_url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        return response

    """
    When a case is created by an user that does not have a organisation then any operator or
    operator managercan register a complaint and EOD against that case.
    """

    def test_operator_can_create_eod_for_cases_created_by_operator_with_no_organisation(self):
        from cla_common.constants import EXPRESSIONS_OF_DISSATISFACTION

        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.no_org_operator.user)
        path = u"%s:eoddetails-detail" % self.API_URL_NAMESPACE
        create_eod_url = reverse(path, args=(), kwargs={"case_reference": case.reference})
        data = {
            "case_reference": case.reference,
            "categories": [{"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False}],
            "notes": "",
        }
        response = self.client.post(create_eod_url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        return response

    """
    All Operator Managers should be able to see that there is a complaint against
    """

    def test_operator_case_creator_different_organisation_eod_response(self):
        # Check the returned response keys when current operator organisation
        # does not match case creator organisation

        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.bar_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        categories = [
            make_recipe(
                "legalaid.eod_details_category", eod_details=eod, category=EXPRESSIONS_OF_DISSATISFACTION.INCORRECT
            ),
            make_recipe(
                "legalaid.eod_details_category",
                eod_details=eod,
                category=EXPRESSIONS_OF_DISSATISFACTION.PASS_TO_PUBLIC,
            ),
            make_recipe(
                "legalaid.eod_details_category", eod_details=eod, category=EXPRESSIONS_OF_DISSATISFACTION.SCOPE
            ),
        ]

        path = u"%s:eoddetails-detail" % self.API_URL_NAMESPACE
        create_eod_url = reverse(path, args=(), kwargs={"case_reference": case.reference})
        response = self.client.get(create_eod_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        expected_dict = {
            "reference": str(eod.reference),
            "categories": [{"id": category.id} for category in categories],
        }
        self.assertDictEqual(expected_dict, json.loads(response.rendered_content))
        return response

    """
    All Operator Managers should be able to see that there is a complaint against
    """

    def test_operator_case_creator_same_organisation_eod_response(self):
        # Check the returned response keys when current operator organisation
        # does matches case creator organisation

        self.operator.organisation = self.foo_org
        self.operator.save()

        case = make_recipe("legalaid.case", created_by=self.foo_org_operator.user)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        categories = [
            make_recipe(
                "legalaid.eod_details_category", eod_details=eod, category=EXPRESSIONS_OF_DISSATISFACTION.INCORRECT
            ),
            make_recipe(
                "legalaid.eod_details_category",
                eod_details=eod,
                category=EXPRESSIONS_OF_DISSATISFACTION.PASS_TO_PUBLIC,
            ),
            make_recipe(
                "legalaid.eod_details_category", eod_details=eod, category=EXPRESSIONS_OF_DISSATISFACTION.SCOPE
            ),
        ]

        path = u"%s:eoddetails-detail" % self.API_URL_NAMESPACE
        create_eod_url = reverse(path, args=(), kwargs={"case_reference": case.reference})
        response = self.client.get(create_eod_url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
        expected_dict = {
            "reference": str(eod.reference),
            "notes": eod.notes,
            "categories": [{"category": category.category, "is_major": category.is_major} for category in categories],
        }
        self.assertDictEqual(expected_dict, json.loads(response.rendered_content))
        return response
