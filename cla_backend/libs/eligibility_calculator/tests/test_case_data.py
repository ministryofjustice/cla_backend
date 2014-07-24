import random
import unittest
from ..models import CaseData
from ..exceptions import PropertyExpectedException
from .fixtures import get_default_case_data


class TestCaseData(unittest.TestCase):

    GROSS_INCOME_FIELDS = [
        'earnings',
        'other_income',
    ]

    GROSS_CAPITAL_FIELDS = [
        'savings',
        'investment_balance',
        'credit_balance',
        'asset_balance',
        'partner_savings',
        'partner_investment_balance',
        'partner_credit_balance',
        'partner_asset_balance'
    ]

    def test_total_income_calculation(self):
        default_data = get_default_case_data(
            you__income__earnings=0,
            you__income__other_income=0)

        cd = CaseData(**default_data)
        ti = cd.total_income
        income = cd.you.income
        gross_income_orig = 0
        for prop in income.PROPERTY_META.keys():
            part = getattr(income, prop, 0)
            gross_income_orig += part

        self.assertEqual(gross_income_orig, ti)

    def test_total_income_calculation_with_partner(self):
        combined_income = 30000
        default_data = get_default_case_data(
            you__income__earnings=10000,
            you__income__other_income=4000,
            partner__income__earnings=10000,
            partner__income__other_income=6000,
            facts__has_partner=True)

        cd = CaseData(**default_data)
        ti = cd.total_income
        income = cd.you.income
        gross_income_orig = income.earnings + income.other_income
        gross_income_orig += cd.partner.income.earnings
        gross_income_orig += cd.partner.income.other_income
        self.assertEqual(gross_income_orig, ti)
        self.assertEqual(combined_income, ti)

    def test_bad_property_set_exception(self):
        cdd = get_default_case_data(foo='bar', bar__baz=24)
        with self.assertRaises(PropertyExpectedException):
            CaseData(**cdd)

    def test_getattr_raises_if_accessing_invalid_prop(self):
        with self.assertRaises(AttributeError):
            cd = CaseData()
            cd.foo

    def test_get_total_income_no_partner(self):
        cdd = get_default_case_data(
            you__income__earnings=265700,
            you__income__other_income=0,
        )
        cd = CaseData(**cdd)
        self.assertFalse(cd.facts.has_partner)
        self.assertEqual(265700, cd.total_income)

    def test_get_total_income_incl_other_no_partner(self):

        earnings = 265700
        other_income = 100

        cdd = get_default_case_data(
            you__income__earnings=earnings,
            you__income__other_income=other_income
        )
        cd = CaseData(**cdd)
        self.assertFalse(cd.facts.has_partner)
        self.assertEqual(265800, cd.total_income)

    # TODO: fix this to check nested properties
    # def test_provide_partner_earnings_required_partner_other_income(self):
    #     with self.assertRaises(PropertyExpectedException):
    #         cdd = get_default_case_data(
    #             you__income__earnings=1,
    #             you__income__other_income=1,
    #             partner__income__earnings=1,
    #             facts__has_partner=True
    #         )
    #         cd = CaseData(**cdd)
    #         cd.total_income

    def test_get_total_income_with_partner(self):
        cdd = get_default_case_data(
            you__income__earnings=265700,
            you__income__other_income=0,
            partner__income__earnings=100,
            partner__income__other_income=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(265800, cd.total_income)

    def test_get_total_income_incl_other_with_partner(self):
        cdd = get_default_case_data(
            you__income__earnings=265700,
            you__income__other_income=100,
            partner__income__earnings=100,
            partner__income__other_income=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(265900, cd.total_income)

    def test_is_partner_disputed_true(self):
        cdd = get_default_case_data(facts__has_partner=True,
                                    facts__is_partner_opponent=True)
        cd = CaseData(**cdd)
        self.assertTrue(cd.facts.has_disputed_partner)

    def test_is_partner_disputed_false(self):
        cdd = get_default_case_data(facts__has_partner=False,
                                    facts__is_partner_opponent=True)
        cd = CaseData(**cdd)
        self.assertFalse(cd.facts.has_disputed_partner)

    def test_is_partner_disputed_not_opponent(self):
        cdd = get_default_case_data(facts__has_partner=True,
                                    facts__is_partner_opponent=False)
        cd = CaseData(**cdd)
        self.assertFalse(cd.facts.has_disputed_partner)

    def test_is_partner_disputed_no_partner_not_opponent(self):
        cdd = get_default_case_data(facts__has_partner=False,
                                    facts__is_partner_opponent=False)
        cd = CaseData(**cdd)
        self.assertFalse(cd.facts.has_disputed_partner)

    def test_get_non_disputed_liquid_capital(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=0,
            you__savings__credit_balance=0,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(0, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_only(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=0,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(10000, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_credit_balance(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=10,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(10010, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_valuable(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=0,
            you__savings__asset_balance=1000,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(11000, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_investment_balance(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=0,
            you__savings__asset_balance=0,
            you__savings__investment_balance=5000,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(15000, cd.non_disputed_liquid_capital)

    # TODO: Fix invalid state check
    # def test_inconsistent_state(self):
    #     cdd = get_default_case_data(
    #         you__savings__bank_balance=10000,
    #         you__savings__credit_balance=0,
    #         you__savings__asset_balance=0,
    #         you__savings__investment_balance=0,
    #         partner__savings__bank_balance=10000,
    #         partner__savings__credit_balance=0,
    #         partner__savings__asset_balance=0,
    #         partner__savings__investment_balance=0,
    #         facts__has_partner=False,
    #     )
    #     with self.assertRaises(InvalidStateException):
    #         cd = CaseData(**cdd)

    def test_get_non_disputed_liquid_capital_savings_with_partner(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=0,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=1,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10001, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_with_partner_credit_balance(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=00,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=20,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10020, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_with_partner_savings(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=00,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=10,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10010, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_with_partner_valuables(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=00,
            you__savings__asset_balance=5000,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(15000, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_with_partner_investment_balance(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=10000,
            you__savings__credit_balance=00,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=100,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10100, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_only_partner_savings(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=0,
            you__savings__credit_balance=0,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=100,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(100, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_only_partner_credit_balance(self):
        cdd = get_default_case_data(
            you__savings__bank_balance=0,
            you__savings__credit_balance=200,
            you__savings__asset_balance=0,
            you__savings__investment_balance=0,
            partner__savings__bank_balance=0,
            partner__savings__credit_balance=0,
            partner__savings__asset_balance=0,
            partner__savings__investment_balance=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(200, cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_random_values_no_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(3):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                you__savings__bank_balance=steps[0],
                you__savings__credit_balance=steps[1],
                you__savings__asset_balance=steps[2],
                you__savings__investment_balance=steps[3],
            )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_random_values_with_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(7):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                you__savings__bank_balance=steps[0],
                you__savings__credit_balance=steps[1],
                you__savings__asset_balance=steps[2],
                you__savings__investment_balance=steps[3],
                partner__savings__bank_balance=steps[4],
                partner__savings__credit_balance=steps[5],
                partner__savings__asset_balance=steps[6],
                partner__savings__investment_balance=steps[7],
                facts__has_partner=True
                )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.non_disputed_liquid_capital)

    def test_get_non_disputed_liquid_capital_savings_random_values_only_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(3):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                you__savings__bank_balance=0,
                you__savings__credit_balance=0,
                you__savings__asset_balance=0,
                you__savings__investment_balance=0,
                partner__savings__bank_balance=steps[0],
                partner__savings__credit_balance=steps[1],
                partner__savings__asset_balance=steps[2],
                partner__savings__investment_balance=steps[3],
                facts__has_partner=True
            )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.non_disputed_liquid_capital)
