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
        'investments',
        'money_owed',
        'valuable_items',
        'partner_savings',
        'partner_investments',
        'partner_money_owed',
        'partner_valuable_items'
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
            gross_income_orig += getattr(income, prop, 0)

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
        gross_income_orig += \
            cd.partner.income.earnings + cd.partner.income.other_income
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
            you__income__other_income=0
        )
        cd = CaseData(**cdd)
        self.assertFalse(cd.facts.has_partner)
        self.assertEqual(265700, cd.total_income)

    def test_get_total_income_incl_other_no_partner(self):
        cdd = get_default_case_data(
            you__income__earnings=265700,
            you__income__other_income=100
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

    def test_get_liquid_capital(self):
        cdd = get_default_case_data(
            you__savings__savings=0,
            you__savings__money_owed=0,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(0, cd.liquid_capital)

    def test_get_liquid_capital_savings_only(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=0,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(10000, cd.liquid_capital)

    def test_get_liquid_capital_savings_money_owed(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=10,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(10010, cd.liquid_capital)

    def test_get_liquid_capital_savings_valuable(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=0,
            you__savings__valuable_items=1000,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(11000, cd.liquid_capital)

    def test_get_liquid_capital_savings_investments(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=0,
            you__savings__valuable_items=0,
            you__savings__investments=5000,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0
        )
        cd = CaseData(**cdd)
        self.assertEqual(15000, cd.liquid_capital)

    # TODO: Fix invalid state check
    # def test_inconsistent_state(self):
    #     cdd = get_default_case_data(
    #         you__savings__savings=10000,
    #         you__savings__money_owed=0,
    #         you__savings__valuable_items=0,
    #         you__savings__investments=0,
    #         partner__savings__savings=10000,
    #         partner__savings__money_owed=0,
    #         partner__savings__valuable_items=0,
    #         partner__savings__investments=0,
    #         facts__has_partner=False,
    #     )
    #     with self.assertRaises(InvalidStateException):
    #         cd = CaseData(**cdd)

    def test_get_liquid_capital_savings_with_partner(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=0,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=1,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10001, cd.liquid_capital)

    def test_get_liquid_capital_savings_with_partner_money_owed(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=00,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=20,
            partner__savings__valuable_items=0,
            partner__savings__investments=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10020, cd.liquid_capital)

    def test_get_liquid_capital_savings_with_partner_savings(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=00,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=10,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10010, cd.liquid_capital)

    def test_get_liquid_capital_savings_with_partner_valuables(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=00,
            you__savings__valuable_items=5000,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(15000, cd.liquid_capital)

    def test_get_liquid_capital_savings_with_partner_investments(self):
        cdd = get_default_case_data(
            you__savings__savings=10000,
            you__savings__money_owed=00,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=100,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(10100, cd.liquid_capital)

    def test_get_liquid_capital_savings_only_partner_savings(self):
        cdd = get_default_case_data(
            you__savings__savings=0,
            you__savings__money_owed=0,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=100,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(100, cd.liquid_capital)

    def test_get_liquid_capital_savings_only_partner_money_owed(self):
        cdd = get_default_case_data(
            you__savings__savings=0,
            you__savings__money_owed=200,
            you__savings__valuable_items=0,
            you__savings__investments=0,
            partner__savings__savings=0,
            partner__savings__money_owed=0,
            partner__savings__valuable_items=0,
            partner__savings__investments=0,
            facts__has_partner=True
        )
        cd = CaseData(**cdd)
        self.assertEqual(200, cd.liquid_capital)

    def test_get_liquid_capital_savings_random_values_no_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(3):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                you__savings__savings=steps[0],
                you__savings__money_owed=steps[1],
                you__savings__valuable_items=steps[2],
                you__savings__investments=steps[3],
            )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.liquid_capital)

    def test_get_liquid_capital_savings_random_values_with_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(7):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                you__savings__savings=steps[0],
                you__savings__money_owed=steps[1],
                you__savings__valuable_items=steps[2],
                you__savings__investments=steps[3],
                partner__savings__savings=steps[4],
                partner__savings__money_owed=steps[5],
                partner__savings__valuable_items=steps[6],
                partner__savings__investments=steps[7],
                facts__has_partner=True
                )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.liquid_capital)

    def test_get_liquid_capital_savings_random_values_only_partner(self):
        for i in range(0, 500):
            # ghetto quick-check
            steps = [random.randint(0, 50000)]
            for n in range(3):
                step = random.randint(0, steps[-1])
                steps.append(step)

            cdd = get_default_case_data(
                you__savings__savings=0,
                you__savings__money_owed=0,
                you__savings__valuable_items=0,
                you__savings__investments=0,
                partner__savings__savings=steps[0],
                partner__savings__money_owed=steps[1],
                partner__savings__valuable_items=steps[2],
                partner__savings__investments=steps[3],
                facts__has_partner=True
            )
            cd = CaseData(**cdd)
            self.assertEqual(sum(steps), cd.liquid_capital)


class GrossIncomeTestCase(unittest.TestCase):

    def test_gross_income(self):
        """
        TEST: Gross income == mocked total income
        """
        pass

    def test_on_passported_benefits_is_gross_income_eligible(self):
        """
        TEST: Gross income not called
        """
        pass

    def test_is_gross_income_eligible(self):
        """
        TEST: eligibility depends on mocked limit
        """
        pass

    def test_is_gross_income_not_eligible(self):
        """
        TEST: eligibility depends on mocked limit
        """
        pass


class DisposableIncomeTestCase(unittest.TestCase):

    def test_disposable_income_with_children(self):
        """
        TEST: with mocked gross_income,
        has_partner = True

        we check that
        disposable capital returns gross_income minus
        allowance for dependent children > 1,
        income_tax_and_ni > 1,
        maintainable > 1
        self employed = False
        mortgage_or_rent > 1
        childcare > 1
        criminal_legalaid_contributions > 1

        should_aggregate_partner = True,
            partner.income_tax_and_ni > 1
            partner.maintenance > 1
            partner.self_employed = False
            partner.childcare > 1
            partner.criminal_legalaid_contributions > 1

        should be equal to sum of above random values

        """
        pass

    def test_disposable_income_single_without_children_below_cap(self):
        """
        TEST: with mocked gross_income,
        has_partner = False
        dependent_children = 0

        we check that
        disposable capital returns gross_income minus
        allowance for dependent children: 0,
        income_tax_and_ni > 1,
        maintainable > 1
        self employed = True
        mortgage_or_rent > 1  (and below childless housing cap)
        childcare > 1
        criminal_legalaid_contributions > 1

        should be equal to sum of above random values

        """
        pass

    def test_disposable_income_single_without_children_above_cap(self):
        """
        TEST: with mocked gross_income,
        has_partner = False
        dependent_children = 0

        we check that
        disposable capital returns gross_income minus
        allowance for dependent children: 0,
        income_tax_and_ni > 1,
        maintainable > 1
        self employed = True
        mortgage_or_rent > 1  (and above childless housing cap)
        childcare > 1
        criminal_legalaid_contributions > 1

        should be equal to sum of above random values

        """
        pass

    def test_on_passported_benefits_is_disposable_income_eligible(self):
        """
        TEST: disposable income not called
        """

        pass

    def test_is_disposable_income_eligible(self):
        """
        TEST: mock disposable income
        """
        pass

    def test_is_disposable_income_not_eligible(self):
        """
        TEST: mock disposable income
        """
        pass


class DisposableCapitalTestCase(unittest.TestCase):

    def test_disposable_capital_assets_over_mortgage_disregard(self):
        """
        TEST: mock liquid capital and property capital, not disputed partner
        property capital over MORTGAGE_DISREGARD
        returns MORTGAGE_DISREGARD,
        """
        pass

    def test_disposable_capital_assets_exactly_equal_mortgage_disregard(self):
        """
        TEST: mock liquid capital and property capital, not disputed partner
        property capital == MORTGAGE_DISREGARD
        asserts property_capital == property_capital
        """
        pass

    def test_disposable_capital_assets_under_mortgage_disregard(self):
        """
        TEST: mock liquid capital and property capital, not disputed partner
        property capital == MORTGAGE_DISREGARD
        asserts property_capital == property_capital
        """
        pass

    def test_disposable_capital_assets_not_negative(self):
        """
        TEST: mock liquid capital and property capital, not disputed partner
        result can't be negative after subtracting equity disregard
        """
        pass

    def test_disposable_capital_assets_subtracts_pensioner_disregard(self):
        """
        TEST: mock liquid capital and property capital, not disputed partner
        property capital mocked to return (0, 0),
        disposable_capital mocked to be > pensioner_disregard
        is_you_or_partner_over_60 = True
        """
        pass

    def test_disposable_capital_assets_subtracts_pensioner_disregard_but_cant_be_negative(self):
        """
        TEST: mock liquid capital and property capital, not disputed partner,
        disposable capital mocked = 0
        property capital mocked to return (0, 0),
        is_you_or_partner_over_60 = True
        """
        pass

    def test_disposable_capital_is_partner_opponent(self):
        """
        Should raise NotImplementedError,
        mock has_disputed_partner = True
        """
        pass
        # with self.assertRaises(NotImplementedError):
        #     pass

    def test_is_disposable_capital_eligible(self):
        """
        TEST: with mocked disposable_capital_assets and get_limit
        """
        pass

    def test_is_disposable_capital_not_eligible(self):
        """
        TEST: with mocked disposable_capital_assets and get_limit
        """
        pass


class IsEligibleTestCase(unittest.TestCase):

    def test_is_disposable_capital_not_eligible(self):
        """
        TEST: with mocked is_disposable_capital_eligible = False
        is_gross_income_eligible, is_disposable_income are not called
        asserts is_eligible = False
        """
        pass

    def test_is_gross_income_not_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = False,
            is_disposable_capital = True

        is_disposable_income is not called
        asserts is_eligible = False
        """
        pass

    def test_is_disposable_income_not_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = True,
            is_disposable_capital = True,
            is_disposable_income = False
        asserts is_eligible = False
        """
        pass

    def test_is_disposable_income_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = True,
            is_disposable_capital = True,
            is_disposable_income = True
        asserts is_eligible = True
        """
        pass
