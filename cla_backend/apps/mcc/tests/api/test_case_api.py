from diagnosis.models import DiagnosisTraversal
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe

from cla_eventlog.models import Log

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin


class MCCSplitCaseTestCase(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(MCCSplitCaseTestCase, self).setUp()

        self.case_category = make_recipe("legalaid.category")
        self.case_matter_type1 = make_recipe("legalaid.matter_type1", category=self.case_category)
        self.case_matter_type2 = make_recipe("legalaid.matter_type2", category=self.case_category)

        self.target_category = make_recipe("legalaid.category")
        self.target_matter_type1 = make_recipe("legalaid.matter_type1", category=self.target_category)
        self.target_matter_type2 = make_recipe("legalaid.matter_type2", category=self.target_category)

        self.resource = make_recipe(
            "legalaid.case",
            reference="AA-1234-5678",
            provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
            eligibility_check=make_recipe("legalaid.eligibility_check", category=self.case_category),
            matter_type1=self.case_matter_type1,
            matter_type2=self.case_matter_type2,
        )

        self.url = self.get_url()

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse("mcc:case-split", args=(), kwargs={"reference": reference})

    def get_default_post_data(self):
        return {
            "category": self.target_category.code,
            "matter_type1": self.target_matter_type1.code,
            "matter_type2": self.target_matter_type2.code,
            "notes": "Notes",
            "internal": False,
        }

    def test_split_successful(self):
        self.assertEqual(Log.objects.count(), 0)

        response = self.client.post(
            self.url,
            data=self.get_default_post_data(),
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        self.assertEqual(Log.objects.count(), 3)

        new_case = self.resource.split_cases.first()
        ref_log = Log.objects.filter(case=new_case)[0]
        self.assertEqual(ref_log.notes, "Notes")

    def test_split_allows_same_category(self):
        data = self.get_default_post_data()
        data.update(
            {
                "category": self.case_category.code,
                "matter_type1": self.case_matter_type1.code,
                "matter_type2": self.case_matter_type2.code,
            }
        )

        response = self.client.post(
            self.url,
            data=data,
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])


class MCCChangeCategoryTestCase(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(MCCChangeCategoryTestCase, self).setUp()

        self.case_category = make_recipe("legalaid.category")
        self.new_category = make_recipe("legalaid.category")

        self.resource = make_recipe(
            "legalaid.case",
            reference="AA-9999-9999",
            provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
            eligibility_check=make_recipe(
                "legalaid.eligibility_check",
                category=self.case_category
            )
        )

        self.resource.diagnosis = DiagnosisTraversal.objects.create_eligible(self.case_category)
        self.resource.save()

        self.url = self.get_url()

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse("mcc:case-category-change", kwargs={"reference": reference})

    def test_change_category_success(self):
        self.assertEqual(Log.objects.count(), 0)

        response = self.client.patch(
            self.url,
            data={
                "category": self.new_category.code,
                "notes": "Changing category via MCC"
            },
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.resource.refresh_from_db()
        eligibility = self.resource.eligibility_check
        eligibility.refresh_from_db()
        self.assertEqual(
            eligibility.category,
            self.new_category
        )

        self.assertIsNotNone(self.resource.diagnosis)

        logs = Log.objects.filter(case=self.resource)
        self.assertEqual(logs.count(), 1)
        log = logs.first()

        self.assertEqual(log.code, "CATEGORY_CHANGED")
        self.assertEqual(log.notes, "Changing category via MCC")
        self.assertEqual(
            log.context,
            {
                "old_category": self.case_category.code,
                "new_category": self.new_category.code,
            }
        )

    def test_change_category_requires_note(self):
        response = self.client.patch(
            self.url,
            data={
                "category": self.new_category.code
            },
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_category_does_not_change_outcome_code(self):
        original_outcome_code = self.resource.outcome_code
        response = self.client.patch(
            self.url,
            data={
                "category": self.new_category.code,
                "notes": "Changing category via MCC"
            },
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.resource.refresh_from_db()
        self.assertEqual(
            self.resource.outcome_code,
            original_outcome_code
        )
