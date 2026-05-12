from django.test import TestCase
import mock

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe, make_user

from cla_provider.forms import SplitCaseForm
from mcc.forms import SplitMCCCaseForm


class SplitMCCCaseFormTestCase(TestCase):
    def build_category_data(self):
        class CatData:
            def __init__(self):
                self.category = make_recipe("legalaid.category")
                self.matter_type1 = make_recipe("legalaid.matter_type1", category=self.category)
                self.matter_type2 = make_recipe("legalaid.matter_type2", category=self.category)

        return CatData()

    def setUp(self):
        self.cat1 = self.build_category_data()
        self.cat2 = self.build_category_data()

        # Provider can deal with cat1 and cat2
        self.provider = make_recipe("cla_provider.provider", law_category=[self.cat1.category, self.cat2.category])
        self.request = mock.MagicMock(user=mock.MagicMock(staff=mock.MagicMock(provider=self.provider)))

        self.eligibility_check = make_recipe("legalaid.eligibility_check", category=self.cat1.category)
        self.case = make_recipe(
            "legalaid.case",
            provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
            eligibility_check=self.eligibility_check,
            matter_type1=self.cat1.matter_type1,
            matter_type2=self.cat1.matter_type2,
        )

    def get_default_data(self, **kwargs):
        defaults = {
            "category": self.cat2.category.code,
            "matter_type1": self.cat2.matter_type1.code,
            "matter_type2": self.cat2.matter_type2.code,
            "internal": True,
        }
        defaults.update(kwargs)
        return defaults

    def test_mcc_allows_same_category(self):
        """
        SplitMCCCaseForm should allow choosing the same category as the case.
        """
        data = self.get_default_data(
            category=self.cat1.category.code,
            matter_type1=self.cat1.matter_type1.code,
            matter_type2=self.cat1.matter_type2.code,
            internal=False,
        )

        form = SplitMCCCaseForm(case=self.case, request=self.request, data=data)
        self.assertTrue(form.is_valid(), msg="Unexpected errors: %s" % form.errors)

    def test_mcc_allows_repeated_split_on_parent_and_child(self):
        """
        Ensure MCC form allows splitting a case that is a child or a parent that has already been split.
        """
        split_data = self.get_default_data(internal=False)
        split_form = SplitCaseForm(case=self.case, request=self.request, data=split_data)
        self.assertTrue(split_form.is_valid(), split_form.errors)

        user = make_user()
        child = split_form.save(user)
        child.refresh_from_db()

        self.case.refresh_from_db()
        parent_mcc_form = SplitMCCCaseForm(case=self.case, request=self.request, data=split_data)
        self.assertTrue(parent_mcc_form.is_valid(), msg="Parent MCC form blocked: %s" % parent_mcc_form.errors)
        parent_mcc_form.save(user)

        child_provider = child.provider
        if child_provider is None:
            child_mcc_form = SplitMCCCaseForm(case=child, request=self.request, data=split_data)
            self.assertFalse(child_mcc_form.is_valid())
            self.assertDictEqual(child_mcc_form.errors, {"__all__": ["Only Providers assigned to the Case can split it."]})
        else:
            child_request = mock.MagicMock(user=mock.MagicMock(staff=mock.MagicMock(provider=child_provider)))
            child_mcc_form = SplitMCCCaseForm(case=child, request=child_request, data=split_data)
            self.assertTrue(child_mcc_form.is_valid(), msg="Child MCC form blocked: %s" % child_mcc_form.errors)
            child_mcc_form.save(user)

    def test_splitcase_still_prevents_same_category_and_repeated_split(self):
        """
        Sanity check: SplitCaseForm still rejects same-category and prevents splitting already-split/child cases.
        """
        data_same = self.get_default_data(
            category=self.cat1.category.code,
            matter_type1=self.cat1.matter_type1.code,
            matter_type2=self.cat1.matter_type2.code,
            internal=False,
        )
        split_form = SplitCaseForm(case=self.case, request=self.request, data=data_same)
        self.assertFalse(split_form.is_valid())
        self.assertIn("category", split_form.errors)

        split_data = self.get_default_data(
            category=self.cat2.category.code,
            matter_type1=self.cat2.matter_type1.code,
            matter_type2=self.cat2.matter_type2.code,
            internal=False,
        )
        split_form_ok = SplitCaseForm(case=self.case, request=self.request, data=split_data)
        self.assertTrue(split_form_ok.is_valid())
        user = make_user()
        child = split_form_ok.save(user)

        child_split_form = SplitCaseForm(case=child, request=self.request, data=split_data)
        self.assertFalse(child_split_form.is_valid())
        self.assertIn("__all__", child_split_form.errors)
