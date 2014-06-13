import unittest
import mock
import random

from ..calculator import EligibilityChecker
from ..models import CaseData
from .. import constants

from . import fixtures

from cla_common.money_interval.models import MoneyInterval

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
        too_little_money = {"interval_period": "per_month",
                            "per_interval_value": constants.gross_income.BASE_LIMIT - 1,
                           }
        case_data = self.get_default_case_data(you__income__earnings=too_little_money)
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertTrue(is_elig)

    def test_gross_income_is_ineligible(self):
        too_much_money = {"interval_period": "per_month",
                         "per_interval_value": constants.gross_income.BASE_LIMIT + 1,
                         }
        case_data = self.get_default_case_data(you__income__earnings=too_much_money)
        is_elig = EligibilityChecker(case_data).is_gross_income_eligible()
        self.assertFalse(is_elig)

    def test_base_limit_gross_income_is_ineligible(self):
        """
        TEST: gross_income limit doesn't rise for 1-4 children.
        Should reject someone for having income more than 2657
        """
        too_much_money = {"interval_period": "per_month",
                          "per_interval_value": constants.gross_income.BASE_LIMIT + 1,
                         }
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
        too_much_money = {"interval_period": "per_month",
                         "per_interval_value": constants.gross_income.BASE_LIMIT + 1,
                         }
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
        case_data = mock.MagicMock()
        type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=True)
        type(case_data).total_income = mock.PropertyMock()
        with mock.patch.object(
                EligibilityChecker,'gross_income',
                new_callable=mock.PropertyMock) as mocked_gross_income:
            ec = EligibilityChecker(case_data)
            self.assertTrue(ec.is_gross_income_eligible())
            self.assertFalse(case_data.total_income.called)
            self.assertFalse(mocked_gross_income.called)

    def test_is_gross_income_eligible_on_limit(self):
        """
        TEST: eligibility depends on mocked limit
        """
        with mock.patch.object(constants, 'gross_income') as mocked_constant_gross_income:
            mocked_constant_gross_income.get_limit.return_value = 500
            case_data = mock.MagicMock()
            type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=False)
            type(case_data.facts).dependant_children = mock.PropertyMock(return_value=0)
            with mock.patch.object(
                    EligibilityChecker,
                    'gross_income',
                    new_callable=mock.PropertyMock) as mocked_gross_income:
                mocked_gross_income.return_value = 500
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_gross_income_eligible())
                mocked_constant_gross_income.get_limit.assert_called_with(0)
                mocked_gross_income.assert_called_once_with()

    def test_is_gross_income_eligible_under_limit(self):
        """
        TEST: eligibility depends on mocked limit
        """
        with mock.patch.object(constants, 'gross_income') as mocked_constant_gross_income:
            mocked_constant_gross_income.get_limit.return_value = 500
            case_data = mock.MagicMock()
            type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=False)
            type(case_data.facts).dependant_children = mock.PropertyMock(return_value=0)
            with mock.patch.object(
                    EligibilityChecker,
                    'gross_income',
                    new_callable=mock.PropertyMock) as mocked_gross_income:
                mocked_gross_income.return_value = 499
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_gross_income_eligible())
                mocked_constant_gross_income.get_limit.assert_called_with(0)
                mocked_gross_income.assert_called_once_with()

    def test_is_gross_income_not_eligible(self):
        """
        TEST: eligibility depends on mocked limit
        """
        with mock.patch.object(constants, 'gross_income') as mocked_constant_gross_income:
            mocked_constant_gross_income.get_limit.return_value = 500
            case_data = mock.MagicMock()
            type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=False)
            type(case_data.facts).dependant_children = mock.PropertyMock(return_value=0)
            with mock.patch.object(
                    EligibilityChecker,
                    'gross_income',
                    new_callable=mock.PropertyMock) as mocked_gross_income:
                mocked_gross_income.return_value = 501
                ec = EligibilityChecker(case_data)
                self.assertFalse(ec.is_gross_income_eligible())
                mocked_constant_gross_income.get_limit.assert_called_with(0)
                mocked_gross_income.assert_called_once_with()


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
                income_tax=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                national_insurance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                maintenance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                mortgage=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                rent=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                childcare=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=False
            )
        )
        partner = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                national_insurance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                maintenance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                mortgage=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                rent=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                childcare=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=False
            )
        )

        case_data = mock.MagicMock(
            facts=facts, you=you, partner=partner
        )

        with mock.patch.object(
            EligibilityChecker, 'gross_income', new_callable=mock.PropertyMock
        ) as mocked_gross_income:

            mocked_gross_income.return_value = random.randint(5000, 100000)

            ec = EligibilityChecker(case_data)

            expected_value = ec.gross_income - \
                constants.disposable_income.PARTNER_ALLOWANCE - \
                facts.dependant_children * constants.disposable_income.CHILD_ALLOWANCE - \
                you.deductions.income_tax['per_month'] - \
                you.deductions.national_insurance['per_month'] - \
                you.deductions.maintenance['per_month'] - \
                you.deductions.mortgage['per_month'] - \
                you.deductions.rent['per_month'] - \
                you.deductions.childcare['per_month'] - \
                you.deductions.criminal_legalaid_contributions - \
                partner.deductions.income_tax['per_month'] - \
                partner.deductions.national_insurance['per_month'] - \
                partner.deductions.maintenance['per_month'] - \
                partner.deductions.mortgage['per_month'] - \
                partner.deductions.rent['per_month'] - \
                partner.deductions.childcare['per_month'] - \
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
                income_tax=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                national_insurance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                maintenance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                mortgage=MoneyInterval('per_month', pennies=constants.disposable_income.CHILDLESS_HOUSING_CAP-1000).as_dict(),
                rent=MoneyInterval('per_month', pennies=0).as_dict(),
                childcare=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=True
            )
        )

        case_data = mock.MagicMock(
            facts=facts, you=you
        )

        with mock.patch.object(
            EligibilityChecker, 'gross_income', new_callable=mock.PropertyMock
        ) as mocked_gross_income:

            mocked_gross_income.return_value = random.randint(5000, 100000)

            ec = EligibilityChecker(case_data)

            expected_value = ec.gross_income - \
                you.deductions.income_tax['per_month'] - \
                you.deductions.national_insurance['per_month'] - \
                you.deductions.maintenance['per_month'] - \
                you.deductions.mortgage['per_month'] - \
                you.deductions.rent['per_month'] - \
                you.deductions.childcare['per_month'] - \
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
                income_tax=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                national_insurance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                maintenance=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                mortgage=MoneyInterval('per_month', pennies=constants.disposable_income.CHILDLESS_HOUSING_CAP+1000,).as_dict(),
                rent=MoneyInterval('per_month', pennies=0).as_dict(),
                childcare=MoneyInterval('per_month', pennies=random.randint(50, 1000)).as_dict(),
                criminal_legalaid_contributions=random.randint(50, 1000)
            ),
            income=mock.MagicMock(
                self_employed=True
            )
        )

        case_data = mock.MagicMock(
            facts=facts, you=you
        )

        with mock.patch.object(
            EligibilityChecker, 'gross_income', new_callable=mock.PropertyMock
        ) as mocked_gross_income:

            mocked_gross_income.return_value = random.randint(5000, 100000)
            ec = EligibilityChecker(case_data)

            expected_value = ec.gross_income - \
                you.deductions.income_tax['per_month'] - \
                you.deductions.national_insurance['per_month'] - \
                you.deductions.maintenance['per_month'] - \
                constants.disposable_income.CHILDLESS_HOUSING_CAP - \
                you.deductions.childcare['per_month'] - \
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

        with mock.patch.object(
            EligibilityChecker, 'gross_income', new_callable=mock.PropertyMock
        ) as mocked_gross_income:

            ec = EligibilityChecker(case_data)

            self.assertTrue(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_gross_income.called, False)

    def test_is_disposable_income_eligible_on_limit(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(
            on_passported_benefits=False
        )
        case_data = mock.MagicMock(facts=facts)

        with mock.patch.object(
            EligibilityChecker, 'disposable_income', new_callable=mock.PropertyMock
        ) as mocked_disposable_income:

            mocked_disposable_income.return_value = constants.disposable_income.LIMIT
            ec = EligibilityChecker(case_data)

            self.assertTrue(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_disposable_income.called, True)

    def test_is_disposable_income_eligible_under_limit(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(
            on_passported_benefits=False
        )
        case_data = mock.MagicMock(facts=facts)

        with mock.patch.object(
            EligibilityChecker, 'disposable_income', new_callable=mock.PropertyMock
        ) as mocked_disposable_income:

            mocked_disposable_income.return_value = constants.disposable_income.LIMIT-1000
            ec = EligibilityChecker(case_data)

            self.assertTrue(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_disposable_income.called, True)

    def test_is_disposable_income_not_eligible(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(
            on_passported_benefits=False
        )
        case_data = mock.MagicMock(facts=facts)

        with mock.patch.object(
            EligibilityChecker, 'disposable_income', new_callable=mock.PropertyMock
        ) as mocked_disposable_income:

            mocked_disposable_income.return_value = constants.disposable_income.LIMIT+1
            ec = EligibilityChecker(case_data)

            self.assertFalse(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_disposable_income.called, True)


class DisposableCapitalTestCase(unittest.TestCase):

    def test_disposable_capital_assets_over_mortgage_disregard(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            mortgages left > MORTGAGE_DISREGARD

        result:
            mortgages left capped to constants.disposable_capital.MORTGAGE_DISREGARD
        """
        facts = mock.MagicMock(
            has_disputed_partner=False,
            is_you_or_your_partner_over_60=False
        )

        properties_value = constants.disposable_capital.MORTGAGE_DISREGARD + \
            constants.disposable_capital.EQUITY_DISREGARD + \
            random.randint(50, 1000)
        mortgages_left = constants.disposable_capital.MORTGAGE_DISREGARD + 1000

        case_data = mock.MagicMock(
            facts=facts,
            liquid_capital=random.randint(50, 1000),
            property_capital=(properties_value, mortgages_left)
        )

        # mocking just to check that PENSIONER_DISREGARD_LIMIT_LEVELS is not called
        with mock.patch.object(
            constants.disposable_capital, 'PENSIONER_DISREGARD_LIMIT_LEVELS'
        ) as mocked_pensioner_disregard:
            ec = EligibilityChecker(case_data)

            expected_value = 0 + \
                case_data.liquid_capital + \
                (
                    case_data.property_capital[0] - \
                    constants.disposable_capital.MORTGAGE_DISREGARD - \
                    constants.disposable_capital.EQUITY_DISREGARD
                )

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, False)

    def test_disposable_capital_assets_exactly_equal_mortgage_disregard(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            mortgages left == MORTGAGE_DISREGARD

        result:
            constants.disposable_capital.MORTGAGE_DISREGARD used
        """
        facts = mock.MagicMock(
            has_disputed_partner=False,
            is_you_or_your_partner_over_60=False
        )

        properties_value = constants.disposable_capital.MORTGAGE_DISREGARD + \
            constants.disposable_capital.EQUITY_DISREGARD + \
            random.randint(50, 1000)
        mortgages_left = constants.disposable_capital.MORTGAGE_DISREGARD

        case_data = mock.MagicMock(
            facts=facts,
            liquid_capital=random.randint(50, 1000),
            property_capital=(properties_value, mortgages_left)
        )

        # mocking just to check that PENSIONER_DISREGARD_LIMIT_LEVELS is not called
        with mock.patch.object(
            constants.disposable_capital, 'PENSIONER_DISREGARD_LIMIT_LEVELS'
        ) as mocked_pensioner_disregard:
            ec = EligibilityChecker(case_data)

            expected_value = 0 + \
                case_data.liquid_capital + \
                (
                    case_data.property_capital[0] - \
                    constants.disposable_capital.MORTGAGE_DISREGARD - \
                    constants.disposable_capital.EQUITY_DISREGARD
                )

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, False)

    def test_disposable_capital_assets_under_mortgage_disregard(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            mortgages left < MORTGAGE_DISREGARD

        result:
            mortgages left used
        """
        facts = mock.MagicMock(
            has_disputed_partner=False,
            is_you_or_your_partner_over_60=False
        )

        properties_value = constants.disposable_capital.MORTGAGE_DISREGARD + \
            constants.disposable_capital.EQUITY_DISREGARD + \
            random.randint(50, 1000)
        mortgages_left = constants.disposable_capital.MORTGAGE_DISREGARD

        case_data = mock.MagicMock(
            facts=facts,
            liquid_capital=random.randint(50, 1000),
            property_capital=(properties_value, mortgages_left)
        )

        # mocking just to check that PENSIONER_DISREGARD_LIMIT_LEVELS is not called
        with mock.patch.object(
            constants.disposable_capital, 'PENSIONER_DISREGARD_LIMIT_LEVELS'
        ) as mocked_pensioner_disregard:
            ec = EligibilityChecker(case_data)

            expected_value = 0 + \
                case_data.liquid_capital + \
                (
                    case_data.property_capital[0] - \
                    mortgages_left - \
                    constants.disposable_capital.EQUITY_DISREGARD
                )

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, False)

    def test_disposable_capital_assets_mortgage_not_negative(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            properties_value == mortgages left == MORTGAGE_DISREGARD

        result:
            EQUITY_DISREGARD not subtracted
        """
        facts = mock.MagicMock(
            has_disputed_partner=False,
            is_you_or_your_partner_over_60=False
        )

        mortgages_left = constants.disposable_capital.MORTGAGE_DISREGARD
        properties_value = mortgages_left

        case_data = mock.MagicMock(
            facts=facts,
            liquid_capital=random.randint(50, 1000),
            property_capital=(properties_value, mortgages_left)
        )

        # mocking just to check that PENSIONER_DISREGARD_LIMIT_LEVELS is not called
        with mock.patch.object(
            constants.disposable_capital, 'PENSIONER_DISREGARD_LIMIT_LEVELS'
        ) as mocked_pensioner_disregard:
            ec = EligibilityChecker(case_data)

            expected_value = case_data.liquid_capital

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, False)

    def test_disposable_capital_assets_subtracts_pensioner_disregard(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            is_you_or_partner_over_60 = True
            properties_value == mortgages left == 0

            liquid_capital > pensioner_disregard

        result:
            disposable_capital = liquid_capital - pensioner_disregard
        """
        facts = mock.MagicMock(
            has_disputed_partner=False,
            is_you_or_your_partner_over_60=True
        )

        case_data = mock.MagicMock(
            facts=facts,
            liquid_capital=random.randint(6000000, 8000000),
            property_capital=(0, 0)
        )

        pensioner_disregard_limit = 5000000
        with mock.patch.object(
            constants.disposable_capital, 'PENSIONER_DISREGARD_LIMIT_LEVELS'
        ) as mocked_pensioner_disregard:
            mocked_pensioner_disregard.get.return_value = pensioner_disregard_limit
            ec = EligibilityChecker(case_data)

            expected_value = case_data.liquid_capital - pensioner_disregard_limit

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, True)

    def test_disposable_capital_assets_subtracts_pensioner_disregard_but_cant_be_negative(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            is_you_or_partner_over_60 = True
            properties_value == mortgages left == 0

            liquid_capital < pensioner_disregard

        result:
            disposable_capital = 0 (no negative numbers returned)
        """
        facts = mock.MagicMock(
            has_disputed_partner=False,
            is_you_or_your_partner_over_60=True
        )

        case_data = mock.MagicMock(
            facts=facts,
            liquid_capital=random.randint(50, 4999999),
            property_capital=(0, 0)
        )

        pensioner_disregard_limit = 5000000
        with mock.patch.object(
            constants.disposable_capital, 'PENSIONER_DISREGARD_LIMIT_LEVELS'
        ) as mocked_pensioner_disregard:
            mocked_pensioner_disregard.get.return_value = pensioner_disregard_limit
            ec = EligibilityChecker(case_data)

            expected_value = 0

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, True)

    #here

    def test_disposable_capital_is_partner_opponent(self):
        """
        Should raise NotImplementedError,
        mock has_disputed_partner = True
        """
        case_data = mock.MagicMock()
        mocked_has_disputed_partner = mock.PropertyMock(return_value=True)
        type(case_data.facts).has_disputed_partner = mocked_has_disputed_partner
        ec = EligibilityChecker(case_data)
        with self.assertRaises(NotImplementedError):
            _ = ec.disposable_capital_assets
        self.assertTrue(mocked_has_disputed_partner.called)

    def test_is_disposable_capital_eligible_under_limit(self):
        """
        TEST: with mocked disposable_capital_assets and get_limit
        """
        with mock.patch.object(constants.disposable_capital, 'get_limit') as mocked_get_limit:
            mocked_get_limit.return_value = 700000
            case_data = mock.MagicMock()
            type(case_data).category = mock.PropertyMock(return_value=u'blah blah')
            with mock.patch.object(
                    EligibilityChecker,
                    'disposable_capital_assets',
                    new_callable=mock.PropertyMock) as mocked_disposable_capital_assets:
                mocked_disposable_capital_assets.return_value = 500
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_disposable_capital_eligible())
                mocked_get_limit.assert_called_once_with(u'blah blah')
                mocked_disposable_capital_assets.assert_called_once_with()

    def test_is_disposable_capital_eligible_on_limit(self):
        """
        TEST: with mocked disposable_capital_assets and get_limit
        """
        with mock.patch.object(constants.disposable_capital, 'get_limit') as mocked_get_limit:
            mocked_get_limit.return_value = 700000
            case_data = mock.MagicMock()
            type(case_data).category = mock.PropertyMock(return_value=u'blah blah')
            with mock.patch.object(
                    EligibilityChecker,
                    'disposable_capital_assets',
                    new_callable=mock.PropertyMock) as mocked_disposable_capital_assets:
                mocked_disposable_capital_assets.return_value = 700000
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_disposable_capital_eligible())
                mocked_get_limit.assert_called_once_with(u'blah blah')
                mocked_disposable_capital_assets.assert_called_once_with()

    def test_is_disposable_capital_not_eligible(self):
        """
        TEST: with mocked disposable_capital_assets and get_limit
        """
        with mock.patch.object(constants.disposable_capital, 'get_limit') as mocked_get_limit:
            mocked_get_limit.return_value = 700000
            case_data = mock.MagicMock()
            type(case_data).category = mock.PropertyMock(return_value=u'blah blah')
            with mock.patch.object(
                    EligibilityChecker,
                    'disposable_capital_assets',
                    new_callable=mock.PropertyMock) as mocked_disposable_capital_assets:
                mocked_disposable_capital_assets.return_value = 700001
                ec = EligibilityChecker(case_data)
                self.assertFalse(ec.is_disposable_capital_eligible())
                mocked_get_limit.assert_called_once_with(u'blah blah')
                mocked_disposable_capital_assets.assert_called_once_with()


class IsEligibleTestCase(unittest.TestCase):

    def test_is_disposable_capital_not_eligible(self):
        """
        TEST: with mocked is_disposable_capital_eligible = False
        is_gross_income_eligible, is_disposable_income are not called
        asserts is_eligible = False
        """
        case_data = mock.MagicMock()
        mocked_on_passported_benefits = mock.PropertyMock()
        type(case_data.facts).on_passported_benefits = mocked_on_passported_benefits
        case_data.facts.on_nass_benefits = False
        ec = EligibilityChecker(case_data)
        ec.is_gross_income_eligible = mock.MagicMock()
        ec.is_disposable_income_eligible = mock.MagicMock()
        ec.is_disposable_capital_eligible = mock.MagicMock(return_value=False)
        self.assertFalse(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        self.assertFalse(ec.is_gross_income_eligible.called)
        self.assertFalse(ec.is_disposable_income_eligible.called)

    def test_is_gross_income_not_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = False,
            is_disposable_capital = True

        is_disposable_income is not called
        asserts is_eligible = False
        """
        case_data = mock.MagicMock()
        mocked_on_passported_benefits = mock.PropertyMock()
        type(case_data.facts).on_passported_benefits = mocked_on_passported_benefits
        case_data.facts.on_nass_benefits = False
        self.assertFalse(mocked_on_passported_benefits.called)
        ec = EligibilityChecker(case_data)
        ec.is_disposable_income_eligible = mock.MagicMock()
        ec.is_gross_income_eligible = mock.MagicMock(return_value=False)
        ec.is_disposable_capital_eligible = mock.MagicMock(return_value=True)

        self.assertFalse(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        ec.is_gross_income_eligible.assert_called_once_with()
        self.assertFalse(ec.is_disposable_income_eligible.called)

    def test_is_disposable_income_not_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = True,
            is_disposable_capital = True,
            is_disposable_income = False
        asserts is_eligible = False
        """
        case_data = mock.MagicMock()
        mocked_on_passported_benefits = mock.PropertyMock()
        type(case_data.facts).on_passported_benefits = mocked_on_passported_benefits
        case_data.facts.on_nass_benefits = False
        self.assertFalse(mocked_on_passported_benefits.called)
        ec = EligibilityChecker(case_data)
        ec.is_disposable_income_eligible = mock.MagicMock(return_value=False)
        ec.is_gross_income_eligible = mock.MagicMock(return_value=True)
        ec.is_disposable_capital_eligible = mock.MagicMock(return_value=True)

        self.assertFalse(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        ec.is_gross_income_eligible.assert_called_once_with()
        ec.is_disposable_capital_eligible.assert_called_once_with()

    def test_is_disposable_income_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = True,
            is_disposable_capital = True,
            is_disposable_income = True
        asserts is_eligible = True
        """
        case_data = mock.MagicMock()
        mocked_on_passported_benefits = mock.PropertyMock()
        type(case_data.facts).on_passported_benefits = mocked_on_passported_benefits
        case_data.facts.on_nass_benefits = False
        self.assertFalse(mocked_on_passported_benefits.called)
        ec = EligibilityChecker(case_data)
        ec.is_disposable_income_eligible = mock.MagicMock(return_value=True)
        ec.is_gross_income_eligible = mock.MagicMock(return_value=True)
        ec.is_disposable_capital_eligible = mock.MagicMock(return_value=True)

        self.assertTrue(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        ec.is_gross_income_eligible.assert_called_once_with()
        ec.is_disposable_capital_eligible.assert_called_once_with()

    def test_nass_benefit_is_eligible(self):
        """
        TEST: if citizen is on NASS benefit income and capital are not
        tested so the citizen should be eligible.
        """
        case_data = mock.MagicMock()
        mocked_on_passported_benefits = mock.PropertyMock()
        type(case_data.facts).on_passported_benefits = mocked_on_passported_benefits
        case_data.facts.on_nass_benefits = True

        ec = EligibilityChecker(case_data)
        self.assertTrue(ec.is_eligible())

