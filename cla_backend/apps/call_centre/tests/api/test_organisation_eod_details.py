from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.models import EODDetails, Case
from cla_eventlog.models import Log
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

    def test_operator_same_organisation_create_eod(self):
        # Only operators matching the case organisation of the same organisation can register an EOD against the case

        case = make_recipe("legalaid.case", organisation=self.foo_org)
        url = reverse(
            u"%s:eoddetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        data = {
            "case_reference": case.reference,
            "categories": [{"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False}],
            "notes": "",
        }

        # (organisation, can_create)
        organisations = [(self.foo_org, True), (self.bar_org, False), (None, False)]
        for organisation, can_create in organisations:
            self.operator.organisation = organisation
            self.operator.save()

            expected_status_code = status.HTTP_201_CREATED if can_create else status.HTTP_403_FORBIDDEN
            response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(expected_status_code, response.status_code)

    def test_operator_same_organisation_update_eod(self):
        # Only operators matching the case organisation of the same organisation can register an EOD against the case

        case = make_recipe("legalaid.case", organisation=self.foo_org)
        eod = make_recipe("legalaid.eod_details", notes="hello", case=case)
        self.assertEqual(eod.categories.count(), 0)
        url = reverse(
            u"%s:eoddetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        data = {
            "reference": str(eod.reference),
            "categories": [
                {"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False},
                {"category": EXPRESSIONS_OF_DISSATISFACTION.PASS_TO_PUBLIC, "is_major": False},
            ],
            "notes": "",
        }

        # (organisation, can_update)
        organisations = [(self.foo_org, True), (self.bar_org, False), (None, False)]
        for organisation, can_update in organisations:
            self.operator.organisation = organisation
            self.operator.save()

            response = self.client.patch(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            expected_status_code = status.HTTP_200_OK if can_update else status.HTTP_403_FORBIDDEN
            self.assertEqual(expected_status_code, response.status_code)
            if can_update:
                eod_reloaded = EODDetails.objects.get(reference=eod.reference)
                self.assertEqual(eod_reloaded.categories.count(), 2)

    def test_any_operator_can_create_eod_against_case_without_organisation(self):
        # Any operator can register an EOD against a case when the case does not have an organisation

        # (organisation, can_create)
        organisations = [(self.foo_org, True), (self.bar_org, True), (None, True)]
        for organisation, can_create in organisations:
            self.operator.organisation = organisation
            self.operator.save()

            case = make_recipe("legalaid.case", organisation=None)
            url = reverse(
                u"%s:eoddetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
            )
            data = {
                "case_reference": case.reference,
                "categories": [{"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False}],
                "notes": "",
            }

            response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            expected_status_code = status.HTTP_201_CREATED if can_create else status.HTTP_403_FORBIDDEN
            self.assertEqual(expected_status_code, response.status_code)

    def test_case_without_organisation_on_eod_details_creation_set_organisation(self):
        # Cases with no organisation are assigned to the current
        # operators organisation when registering an eod against a case

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
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        case_reloaded = Case.objects.get(pk=case.id)
        self.assertEqual(self.foo_org.id, case_reloaded.organisation.id)
        self.assertIn(("CASE_ORGANISATION_SET",), Log.objects.filter(case_id=case.id).values_list("code"))

        self.operator_manager.organisation = self.bar_org
        self.operator_manager.save()

        data["reference"] = response.data.get("reference")
        del data["case_reference"]
        response = self.client.patch(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_cla_superuser_can_update_eod_details(self):
        self.operator_manager.organisation = None
        self.operator_manager.is_cla_superuser = True
        self.operator_manager.save()

        case = make_recipe("legalaid.case", organisation=self.foo_org)
        url = reverse(
            u"%s:eoddetails-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"case_reference": case.reference}
        )
        data = {
            "case_reference": case.reference,
            "categories": [{"category": EXPRESSIONS_OF_DISSATISFACTION.INCORRECT, "is_major": False}],
            "notes": "",
        }
        response = self.client.post(url, data, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.manager_token)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_all_operators_case_can_see_eod_details_count(self):
        # All Operator should be able to see that there is a EOD against
        # Even if the case belongs to another organisation.

        case = make_recipe("legalaid.case", organisation=self.bar_org)
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

        url = reverse(u"%s:case-detail" % self.API_URL_NAMESPACE, args=(), kwargs={"reference": case.reference})

        # (organisation, eod_details_editable)
        organisations = [(self.foo_org, False), (self.bar_org, True), (None, False)]
        for organisation, eod_details_editable in organisations:
            self.operator.organisation = organisation
            self.operator.save()

            response = self.client.get(url, format="json", HTTP_AUTHORIZATION="Bearer %s" % self.token)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data.get("eod_details_count"), len(categories))
            self.assertEqual(response.data.get("eod_details_editable"), eod_details_editable)
