import unittest
import mock
import random

from ..calculator import EligibilityChecker
from ..models import CaseData
from .. import constants

from . import fixtures

class CalculatorTestBase(unittest.TestCase):

    def get_default_case_data(self, **kwargs):
        """
        gives default case_data with each kwarg
        overridden

        :param kwargs: things to overwrite in the default case_data
        :return: CaseData object with default values
        """
        return CaseData(**fixtures.get_default_case_data(**kwargs))


class TestCalculator(CalculatorTestBase):


    def setUp(self):
        self.default_calculator = EligibilityChecker(self.get_default_case_data())

    def test_gross_income_is_eligible(self):
        too_little_money = constants.gross_income.BASE_LIMIT - 1
        case_data = self.get_default_case_data(you__income__earnings=too_little_money)
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertTrue(is_elig)

    def test_gross_income_is_ineligible(self):
        too_much_money = constants.gross_income.BASE_LIMIT + 1
        case_data = self.get_default_case_data(you__income__earnings=too_much_money)
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertFalse(is_elig)

    def test_base_limit_gross_income_is_ineligible(self):
        """
        TEST: gross_income limit doesn't rise for 1-4 children.
        Should reject someone for having income more than 2657
        """
        too_much_money = constants.gross_income.BASE_LIMIT + 1
        for dep_children in range(1,constants.gross_income.INCLUSIVE_CHILDREN_BASE+1):
            case_data = self.get_default_case_data(
                you__income__earnings=too_much_money,
                facts__dependant_children=dep_children
            )
            is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
            self.assertFalse(is_elig)

    def test_base_limit_gross_income_is_eligible(self):
        """
        if you have > 4 children then earning 1 more than base limit
        should be fine.
        """
        too_much_money = constants.gross_income.BASE_LIMIT + 1
        case_data = self.get_default_case_data(
            you__income__earnings=too_much_money,
            facts__dependant_children=5
        )
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertTrue(is_elig)



class TestApplicantOnBenefitsCalculator(CalculatorTestBase):
    """
    An applicant on passported benefits should be eligible
    solely on their disposable capital income test.

    They should not be asked income questions.
    """

    def test_applicant_on_single_benefits_no_capital_is_eligible(self):

        case_data = self.get_default_case_data(
            facts__on_passported_benefits=True,
        )
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        self.assertEqual(case_data.you.income.total, 0)
        self.assertEqual(case_data.total_income, 0)
        self.assertTrue(is_elig)

    def test_applicant_on_single_benefits_no_capital_has_property_is_eligible(self):
        case_data = self.get_default_case_data(
            facts__on_passported_benefits=True,
            property_data=[(10800000, 0, 100,)]
            )
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        self.assertEqual(case_data.you.income.total, 0)
        self.assertEqual(case_data.total_income, 0)
        self.assertTrue(is_elig)


class GrossIncomeTestCase(CalculatorTestBase):
    def test_gross_income(self):
        """
        TEST: Gross income == mocked total income
        """
        case_data = mock.MagicMock(total_income=500)
        ec = EligibilityChecker(case_data)
        self.assertEqual(ec.gross_income, 500)

    def test_on_passported_benefits_is_gross_income_eligible(self):
        """
        TEST: Gross income not called
        """
        # case_data = mock.MagicMock(facts={'on_passported_benefits': True})
        # ec = EligibilityChecker(case_data)
        # ec.is_gross_income_eligible()
        # case_data.facts.assert_has_calls()
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
        facts = mock.MagicMock(
            has_partner=True,
            dependant_children=random.randint(2, 5),
            should_aggregate_partner=True
        )
        you = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax_and_ni=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage_or_rent=random.randint(50, 1000),
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=False
            )
        )
        partner = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax_and_ni=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage_or_rent=random.randint(50, 1000),
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=False
            )
        )

        case_data = mock.MagicMock(
            facts=facts, you=you, partner=partner
        )

        ec = EligibilityChecker(case_data)
        type(ec).gross_income = mock.PropertyMock(
            return_value=random.randint(5000, 100000)
        )

        expected_value = ec.gross_income - \
            constants.disposable_income.PARTNER_ALLOWANCE - \
            facts.dependant_children * constants.disposable_income.CHILD_ALLOWANCE - \
            you.deductions.income_tax_and_ni - \
            you.deductions.maintenance - \
            you.deductions.mortgage_or_rent - \
            you.deductions.childcare - \
            you.deductions.criminal_legalaid_contributions - \
            partner.deductions.income_tax_and_ni - \
            partner.deductions.maintenance - \
            partner.deductions.mortgage_or_rent - \
            partner.deductions.childcare - \
            partner.deductions.criminal_legalaid_contributions - \
            constants.disposable_income.EMPLOYMENT_COSTS_ALLOWANCE - \
            constants.disposable_income.EMPLOYMENT_COSTS_ALLOWANCE

        self.assertEqual(expected_value, ec.disposable_income)

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
        facts = mock.MagicMock(
            has_partner=False,
            dependant_children=0,
            should_aggregate_partner=False
        )
        you = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax_and_ni=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage_or_rent=constants.disposable_income.CHILDLESS_HOUSING_CAP-1000,
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=True
            )
        )

        case_data = mock.MagicMock(
            facts=facts, you=you
        )

        ec = EligibilityChecker(case_data)
        type(ec).gross_income = mock.PropertyMock(
            return_value=random.randint(5000, 100000)
        )

        expected_value = ec.gross_income - \
            you.deductions.income_tax_and_ni - \
            you.deductions.maintenance - \
            you.deductions.mortgage_or_rent - \
            you.deductions.childcare - \
            you.deductions.criminal_legalaid_contributions

        self.assertEqual(expected_value, ec.disposable_income)

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

        Mortgage or rent is capped to
            constants.disposable_income.CHILDLESS_HOUSING_CAP
        """
        facts = mock.MagicMock(
            has_partner=False,
            dependant_children=0,
            should_aggregate_partner=False
        )
        you = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax_and_ni=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage_or_rent=constants.disposable_income.CHILDLESS_HOUSING_CAP+1000,
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=True
            )
        )

        case_data = mock.MagicMock(
            facts=facts, you=you
        )

        ec = EligibilityChecker(case_data)
        type(ec).gross_income = mock.PropertyMock(
            return_value=random.randint(5000, 100000)
        )

        expected_value = ec.gross_income - \
            you.deductions.income_tax_and_ni - \
            you.deductions.maintenance - \
            constants.disposable_income.CHILDLESS_HOUSING_CAP - \
            you.deductions.childcare - \
            you.deductions.criminal_legalaid_contributions

        self.assertEqual(expected_value, ec.disposable_income)

    def test_on_passported_benefits_is_disposable_income_eligible(self):
        """
        TEST: disposable income not called
        """
        facts = mock.MagicMock(
            on_passported_benefits=True
        )
        case_data = mock.MagicMock(facts=facts)

        ec = EligibilityChecker(case_data)
        type(ec).disposable_income = mock.PropertyMock()

        self.assertTrue(ec.is_disposable_income_eligible())
        self.assertEqual(ec.disposable_income.called, False)

    def test_is_disposable_income_eligible(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(
            on_passported_benefits=False
        )
        case_data = mock.MagicMock(facts=facts)

        ec = EligibilityChecker(case_data)
        type(ec).disposable_income = mock.PropertyMock(
            return_value=constants.disposable_income.LIMIT
        )

        self.assertTrue(ec.is_disposable_income_eligible())

    def test_is_disposable_income_not_eligible(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(
            on_passported_benefits=False
        )
        case_data = mock.MagicMock(facts=facts)

        ec = EligibilityChecker(case_data)
        type(ec).disposable_income = mock.PropertyMock(
            return_value=constants.disposable_income.LIMIT+1
        )

        self.assertFalse(ec.is_disposable_income_eligible())


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
