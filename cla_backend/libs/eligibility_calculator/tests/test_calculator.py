# coding=utf-8
import unittest

import mock
import test_vcr

from . import fixtures
from ..calculator import EligibilityChecker
from ..models import CaseData, Income, Deductions


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

    @test_vcr.use_vcr_cassette
    def test_full_case(self):
        # yes it will be brittle, but let's have *one* complete case tested
        case_data_dict = {
            "category": "family",
            "facts": {
                "is_you_or_your_partner_over_60": False,
                "on_passported_benefits": False,
                "on_nass_benefits": False,
                "has_partner": True,
                "is_partner_opponent": False,
                "dependants_young": 1,
                "dependants_old": 1,
                "under_18_passported": False,
                "is_you_under_18": False,
                "under_18_receive_regular_payment": False,
                "under_18_has_valuables": False,
            },
            "you": {
                "income": {
                    "earnings": 90000,
                    "self_employment_drawings": 5,
                    "benefits": 7,
                    "tax_credits": 11,
                    "child_benefits": 13,
                    "maintenance_received": 19,
                    "pension": 23,
                    "other_income": 29,
                    "self_employed": False,
                },
                "savings": {"bank_balance": 3, "investment_balance": 5, "credit_balance": 7, "asset_balance": 9},
                "deductions": {
                    "income_tax": 1,
                    "national_insurance": 2,
                    "maintenance": 3,
                    "mortgage": 4,
                    "rent": 5,
                    "childcare": 6,
                    "criminal_legalaid_contributions": 7,
                },
            },
            "partner": {
                "income": {
                    "earnings": 13,
                    "self_employment_drawings": 15,
                    "benefits": 17,
                    "tax_credits": 21,
                    "child_benefits": 23,
                    "maintenance_received": 29,
                    "pension": 33,
                    "other_income": 39,
                    "self_employed": False,
                },
                "savings": {"bank_balance": 13, "investment_balance": 15, "credit_balance": 17, "asset_balance": 19},
                "deductions": {
                    "income_tax": 11,
                    "national_insurance": 12,
                    "maintenance": 13,
                    "mortgage": 14,
                    "rent": 15,
                    "childcare": 16,
                    "criminal_legalaid_contributions": 17,
                },
            },
            "property_data": [
                {"disputed": False, "main": True, "value": 20000000, "mortgage_left": 5000000, "share": 50},
            ],
        }
        case_data = CaseData(**case_data_dict)
        checker = EligibilityChecker(case_data=case_data)

        result, calcs, cfe_response = checker._do_cfe_civil_check()

        self.assertEqual("yes", result)
        # the calcs are a bit contrived, so instead we check the CFE key totals
        response_data = cfe_response._cfe_data

        # gross income
        expected_gross_income = 90000 + 5 + 7 + 11 + 13 + 19 + 23 + 29 + 13 + 15 + 17 + 21 + 23 + 29 + 33 + 39
        self.assertEqual(
            expected_gross_income, response_data["result_summary"]["gross_income"]["combined_total_gross_income"] * 100
        )

        # disposable income
        # CFE's calculation will change over time, so try to use constants supplied by CFE as much as possible to avoid test breaking
        expected_disposable_income = expected_gross_income
        expected_disposable_income -= 1 + 2 + 3 + 4 + 5 + 6 + 7 + 11 + 12 + 13 + 14 + 15 + 16 + 17  # deductions
        expected_disposable_income -= calcs["employment_allowance"] * 2  # £45 for both client and partner
        expected_disposable_income -= calcs["partner_allowance"]  # value may change over time
        dependant_allowances_applied = response_data["result_summary"]["disposable_income"]["dependant_allowance"]
        assert dependant_allowances_applied > 0
        expected_disposable_income -= dependant_allowances_applied * 100
        self.assertEqual(
            expected_disposable_income,
            response_data["result_summary"]["disposable_income"]["combined_total_disposable_income"] * 100,
        )

        # capital
        property_capital = (20000000 - 5000000) * 0.5
        # property is all disregarded
        self.assertEqual(
            property_capital,
            response_data["assessment"]["capital"]["capital_items"]["properties"]["main_home"][
                "main_home_equity_disregard"
            ]
            * 100,
        )
        expected_capital = 3 + 5 + 7 + 9 + 13 + 15 + 17 + 19  # savings
        self.assertEqual(
            expected_capital, response_data["result_summary"]["capital"]["combined_assessed_capital"] * 100
        )


class TestApplicantOnBenefitsCalculator(CalculatorTestBase):
    """
    An applicant on passported benefits should be eligible
    solely on their disposable capital income test.

    They should not be asked income questions.
    """

    def test_applicant_on_single_benefits_no_capital_is_eligible(self):
        case_data = self.get_default_case_data(facts__on_passported_benefits=True)
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        self.assertEqual(case_data.you.income.total, 0)
        self.assertEqual(case_data.total_income, 0)
        self.assertTrue(is_elig)
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 0,
                "disposable_capital_assets": 0,
                "property_equities": [0],
                "property_capital": 0,
                "non_property_capital": 0,
                "disposable_income": 0,
                "employment_allowance": 0,
                "gross_income": 0,
                "partner_allowance": 0,
                "dependants_allowance": 0,
                "partner_employment_allowance": 0,
            },
        )

    def test_applicant_on_single_benefits_no_capital_has_property_is_eligible(self):
        case_data = self.get_default_case_data(
            facts__on_passported_benefits=True,
            property_data=[{"value": 10800000, "mortgage_left": 0, "share": 100, "disputed": False, "main": True}],
        )
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        self.assertEqual(case_data.you.income.total, 0)
        self.assertEqual(case_data.total_income, 0)
        self.assertTrue(is_elig)
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 0,
                "disposable_capital_assets": 800000,
                "property_equities": [800000],
                "property_capital": 800000,
                "non_property_capital": 0,
                "gross_income": 0,
                "partner_allowance": 0,
                "disposable_income": 0,
                "dependants_allowance": 0,
                "employment_allowance": 0,
                "partner_employment_allowance": 0,
            },
        )


class TestApplicantPensionerCoupleOnBenefits(CalculatorTestBase):
    def _test_pensioner_on_benefits(self, property_value, mortgage, other_assets):
        case_data = self.get_default_case_data(
            facts__on_passported_benefits=True,
            facts__is_you_or_your_partner_over_60=True,
            property_data=[
                {"value": property_value, "mortgage_left": mortgage, "share": 100, "disputed": False, "main": True}
            ],
        )
        case_data.you.savings.asset_balance = other_assets

        return EligibilityChecker(case_data)

    def test_pensioner_250k_house_100k_mort_0_savings(self):
        """
        if over 60 and on benefits 250k house with 100k mortgage should pass
        """
        checker = self._test_pensioner_on_benefits(25000000, 10000000, 0)
        self.assertTrue(checker.is_eligible())
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 10000000,
                "gross_income": 0,
                "partner_allowance": 0,
                "disposable_income": 0,
                "dependants_allowance": 0,
                "employment_allowance": 0,
                "partner_employment_allowance": 0,
                "property_capital": 5000000,
                "property_equities": [5000000],
                "non_property_capital": 0,
                "disposable_capital_assets": 0,
            },
        )

    def test_pensioner_300k1p_house_100k1p_mort_799999_savings(self):
        """
        if over 60 and on benefits, 300K.01 house with 100K.01 mortgage and
        7999.99 of other assets should pass.
        """
        checker = self._test_pensioner_on_benefits(30000001, 10000001, 79999)
        expected_results = {
            "pensioner_disregard": 10000000,
            "gross_income": 0,
            "partner_allowance": 0,
            "disposable_income": 0,
            "dependants_allowance": 0,
            "employment_allowance": 0,
            "partner_employment_allowance": 0,
            "non_property_capital": 79999,
        }
        expected_property_results = {
            "property_capital": 10000000,
            "property_equities": [10000000],
            "disposable_capital_assets": 79999,
        }
        expected_results.update(expected_property_results)
        self.assertTrue(checker.is_eligible())
        self.assertDictEqual(checker.calcs, expected_results)

    def test_pensioner_300k2p_house_100k1p_mort_799999_savings(self):
        """
        if over 60 and on benefits, 300K.02 house with 100K.01 mortgage and
        7999.99 of other assets should fail.
        """
        checker = self._test_pensioner_on_benefits(30000002, 10000001, 79999)

        expected_results = {
            "pensioner_disregard": 10000000,
            "gross_income": 0,
            "partner_allowance": 0,
            "disposable_income": 0,
            "dependants_allowance": 0,
            "employment_allowance": 0,
            "partner_employment_allowance": 0,
            "non_property_capital": 79999,
        }
        expected_property_results = {
            "property_capital": 10000001,
            "property_equities": [10000001],
            "disposable_capital_assets": 80000,
        }
        expected_results.update(expected_property_results)

        self.assertTrue(checker.is_eligible())
        self.assertDictEqual(checker.calcs, expected_results)


class TestApplicantSinglePensionerNotOnBenefits(CalculatorTestBase):
    def _test_pensioner(self, case_data):
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        return is_elig, checker

    def test_pensioner_200k2p_house_100k1p_mort_800001_savings(self):
        """
        if over 60 and not on benefits, 200K.02 house with 100K.01 mortgage and
        8000.01+.01+.01 of other assets should fail.
        """

        case_data = self.get_default_case_data(
            facts__on_passported_benefits=False,
            facts__is_you_or_your_partner_over_60=True,
            property_data=[
                {"value": 20000002, "mortgage_left": 10000001, "share": 100, "disputed": False, "main": True}
            ],
            you__income__earnings=31606,  # Increased value by 100 pence because of the bug in CFE's pensioner capital disregards threshold (https://dsdmoj.atlassian.net/browse/LEP-462)
            you__income__other_income=59001,
            you__savings__bank_balance=800001,
            you__savings__investment_balance=1,
            you__savings__asset_balance=1,
            you__savings__credit_balance=1,
            you__deductions__mortgage=54501,
            you__deductions__rent=2,
            you__deductions__income_tax=2,
            you__deductions__national_insurance=1,
            you__deductions__maintenance=1,
            you__deductions__childcare=1,
            you__deductions__criminal_legalaid_contributions=1,
        )
        is_elig, checker = self._test_pensioner(case_data)

        expected_results = {
            "pensioner_disregard": 0,
            "gross_income": 90607,
            "partner_allowance": 0,
            "disposable_income": 31602,  # Value updated because "childcare" should be deducted from gross_income only if dependants are present. Currently, dependant count check is missing in CLA while deducting childcare
            "dependants_allowance": 0,
            "employment_allowance": 4500,
            "partner_employment_allowance": 0,
            "non_property_capital": 800004,  # "liquid_capital" is defined as "non property capital", so should include "asset_balance" and "credit_balance" (i.e non_liquid_capital)
        }
        expected_property_results = {
            "property_capital": 1,
            "property_equities": [1],
            "disposable_capital_assets": 800005,
        }
        expected_results.update(expected_property_results)

        self.assertEqual("no", is_elig)
        self.assertDictEqual(expected_results, checker.calcs)

    def test_pensioner_limit_10k_diregard_fail(self):
        """
        pensioner over 60, no property 18,000.01 savings
        310 other income:
        should be ineligible.
        """
        case_data = self.get_default_case_data(
            facts__on_passported_benefits=False,
            facts__is_you_or_your_partner_over_60=True,
            you__income__other_income=31000,
            you__savings__bank_balance=1800001,
        )

        is_elig, checker = self._test_pensioner(case_data)

        self.assertEqual("no", is_elig)
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 1000000,
                "gross_income": 31000,
                "partner_allowance": 0,
                "disposable_income": 31000,
                "dependants_allowance": 0,
                "employment_allowance": 0,
                "partner_employment_allowance": 0,
                "property_capital": 0,
                "property_equities": [0],
                "non_property_capital": 1800001,
                "disposable_capital_assets": 800001,
            },
        )


class IsEligibleTestCase(unittest.TestCase):
    def create_a_dummy_citizen(
        self,
        is_category=False,
        is_passported=None,
        is_nass_benefits=None,
        is_gross_income=None,
        is_disposable_income=None,
        is_disposable_capital=None,
        has_passported_proceedings_letter=None,
        is_under_18_passported=None,
    ):
        # gross_income, disposable_income, disposable_capital
        """
        This method creates a dummy citizen to use in the eligibility tests for legal aid.
        Set the category to either immigration, any other category or let it default to False.
        Set their passported benefits to either True, False or default to None.
        Set their NASS benefits to either True, False or default to None.
        Set their gross income to True (they are eligible), False (they are not eligible), or default to None.
        Set their disposable income to True (they are eligible), False (they are not eligible), or default to None.
        Set their disposable capital to True (they are eligible), False (they are not eligible), or default to None.
        """
        case_data = CaseData(**fixtures.get_default_case_data())
        case_data.category = is_category
        case_data.facts = mock.MagicMock()
        case_data.facts.has_passported_proceedings_letter = has_passported_proceedings_letter
        case_data.facts.under_18_passported = is_under_18_passported
        mocked_on_passported_benefits = mock.PropertyMock(return_value=is_passported)
        mocked_on_nass_benefits = mock.PropertyMock(return_value=is_nass_benefits)
        type(case_data.facts).on_passported_benefits = mocked_on_passported_benefits
        type(case_data.facts).on_nass_benefits = mocked_on_nass_benefits
        ec = EligibilityChecker(case_data)
        ec.is_gross_income_eligible = mock.MagicMock(return_value=is_gross_income)
        ec.is_disposable_income_eligible = mock.MagicMock(return_value=is_disposable_income)
        ec.is_disposable_capital_eligible = mock.MagicMock(return_value=is_disposable_capital)
        return ec, mocked_on_passported_benefits, mocked_on_nass_benefits


class DoCfeCivilCheckTestCase(unittest.TestCase):
    def checker_with_category(self, category="family"):
        cd = fixtures.get_default_case_data()
        cd.update({"category": category})
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def checker_with_facts_without_defaults(self, facts, partner=None):
        cd = fixtures.get_default_case_data()
        cd["facts"] = facts
        if partner is not None:
            cd["partner"] = partner
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def checker_with_facts(self, facts, partner=None):
        cd = fixtures.get_default_case_data()
        cd["facts"].update(facts)
        if partner is not None:
            cd["partner"] = partner
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def savings_dict(self, assets, bank=0):
        return dict(bank_balance=bank, asset_balance=assets, investment_balance=0, credit_balance=0)

    def checker_with_facts_and_income(
        self,
        on_passported_benefits=False,
        on_nass_benefits=False,
        under_18_passported=True,
        is_you_under_18=True,
        income=0,
    ):
        cd = fixtures.get_default_case_data()
        cd["facts"].update(
            {
                "on_passported_benefits": on_passported_benefits,
                "on_nass_benefits": on_nass_benefits,
                "under_18_passported": under_18_passported,
                "is_you_under_18": is_you_under_18,
            }
        )
        cd["you"].update(
            {
                "income": dict(
                    earnings=income,
                    self_employed=False,
                    maintenance_received=0,
                    child_benefits=0,
                    tax_credits=0,
                    pension=0,
                    benefits=0,
                    other_income=0,
                ),
                "deductions": dict(income_tax=500, national_insurance=200),
            }
        )
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def checker_with_assets(self, assets, facts=None):
        cd = self.case_dict_with_property(facts=facts)
        cd["you"].update({"savings": self.savings_dict(assets)})
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def checker_with_disputed_assets(self, assets, savings=None):
        cd = self.case_dict_with_property()
        cd.update({"disputed_savings": self.savings_dict(assets)})
        if savings is not None:
            cd["you"].update({"savings": savings})
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_no_assets(self):
        result, _, cfe_response = self.checker_with_assets(0)._do_cfe_civil_check()
        self.assertEqual("eligible", cfe_response.overall_result)
        self.assertEqual("yes", result)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_too_much_savings(self):
        result, _, cfe_response = self.checker_with_assets(1000000)._do_cfe_civil_check()
        self.assertEqual("ineligible", cfe_response.overall_result)
        self.assertEqual("no", result)

    def case_dict_with_property(self, value=10000, facts=None):
        property_data = [{"value": value * 100, "mortgage_left": 0, "share": 100, "disputed": False, "main": True}]
        if facts is None:
            return fixtures.get_default_case_data(property_data=property_data)
        else:
            return fixtures.get_default_case_data(property_data=property_data, facts=facts)

    def checker_with_property(self, value):
        cd = self.case_dict_with_property(value)
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def checker_with_blank_property(self):
        property_data = [{}]
        cd = fixtures.get_default_case_data(property_data=property_data)
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_small_property(self):
        _, _, cfe_response = self.checker_with_property(100000)._do_cfe_civil_check()
        self.assertEqual("eligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_large_property(self):
        _, _, cfe_response = self.checker_with_property(300000)._do_cfe_civil_check()
        self.assertEqual("ineligible", cfe_response.overall_result)

    def checker_with_income(self, income, tax, ni=600, self_employed=False):
        cd = fixtures.get_default_case_data()
        cd["you"].update(
            {
                "income": dict(
                    earnings=income,
                    self_employed=self_employed,
                    maintenance_received=0,
                    child_benefits=0,
                    tax_credits=0,
                    pension=0,
                    benefits=0,
                    other_income=0,
                ),
                "deductions": dict(income_tax=tax, national_insurance=ni),
            }
        )
        self.income_sections_are_completed(cd)
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def checker_with_income_without_earnings(
        self, maintenance_received, child_benefits, deductions=None, self_employed=False, tax_credits=0
    ):
        # NB this doesn't 'complete' the case with a call self.income_sections_are_completed(),
        # so is likely to return an 'unknown' result
        cd = self.case_dict_with_property(10000)
        if tax_credits is None:
            cd["you"].update(
                {
                    "income": dict(
                        self_employed=self_employed,
                        earnings=0,
                    ),
                }
            )
        else:
            cd["you"].update(
                {
                    "income": dict(
                        self_employed=self_employed,
                        maintenance_received=maintenance_received,
                        child_benefits=child_benefits,
                        tax_credits=0,
                        pension=0,
                        benefits=0,
                        other_income=0,
                    ),
                }
            )
        if deductions is not None:
            cd["you"].update({"deductions": deductions})
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    @test_vcr.use_vcr_cassette
    def test_income_complete_without_child_benefit(self):
        # Tests the circumstance, of child_benefit field is removed, but should still be considered complete.
        # This is encountered in cla_public, if you say yes to benefits but don't check "child benefit" checkbox.
        cd = fixtures.get_default_case_data()
        del cd["you"]["income"]["child_benefits"]
        # Deliberately not calling self.income_sections_are_completed(cd)
        case_data = CaseData(**cd)
        cfe_result, _, _ = EligibilityChecker(case_data=case_data)._do_cfe_civil_check()
        self.assertEqual("yes", cfe_result)

    def checker_with_deductions(self, income, deductions):
        cd = fixtures.get_default_case_data()
        cd["you"].update(
            {
                "income": dict(
                    earnings=income,
                    self_employed=False,
                    maintenance_received=0,
                    child_benefits=0,
                    tax_credits=0,
                    pension=0,
                    benefits=0,
                    other_income=0,
                ),
                "deductions": deductions,
            }
        )
        self.income_sections_are_completed(cd)
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def income_sections_are_completed(self, case_data):
        """
        Ensure case_data is "complete" in terms of gross & disposable income
        i.e. add some properties that we expect to exist if the frontends have asked all the relevant questions on income.
        This emulates what would be done by cla_public and cla_frontend.
        """
        for key in Income.PROPERTY_META:
            if key not in case_data["you"]["income"]:
                case_data["you"]["income"][key] = 0
        for key in Deductions.PROPERTY_META:
            if key not in case_data["you"]["deductions"]:
                case_data["you"]["deductions"][key] = 0

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_small_gross_income(self):
        # income is in pence
        _, _, cfe_response = self.checker_with_income(10000, 100)._do_cfe_civil_check()
        self.assertEqual(45.0, cfe_response.employment_allowance)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_self_employed(self):
        _, _, cfe_response = self.checker_with_income(10000, 100, self_employed=True)._do_cfe_civil_check()
        self.assertEqual(0.0, cfe_response.employment_allowance)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_large_gross_income(self):
        _, _, cfe_response = self.checker_with_income(1000000, 500)._do_cfe_civil_check()
        self.assertEqual("ineligible", cfe_response.overall_result)

    def checker_with_dependants(self, young_count, old_count):
        cd = self.case_dict_with_property(10000)
        cd["facts"].update(dict(dependants_old=old_count, dependants_young=young_count))
        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    def do_cfe_civil_check(self, checker):
        _, _, cfe_result = checker._do_cfe_civil_check()
        return cfe_result

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_no_dependants(self):
        checker = self.checker_with_dependants(0, 0)
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_many_young_dependants_increases_gross_threshold(self):
        checker = self.checker_with_dependants(6, 0)
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertEqual(3101.0, cfe_result.gross_upper_threshold)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_many_old_dependants_doesnt_change_gross_threshold(self):
        checker = self.checker_with_dependants(0, 6)
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertEqual(2657.0, cfe_result.gross_upper_threshold)

    @test_vcr.use_vcr_cassette
    def test_small_income_without_earnings_cfe_eligible(self):
        checker = self.checker_with_income(income=10000, tax=500)
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_large_income_without_earnings_cfe_ineligible(self):
        checker = self.checker_with_income(income=100000, tax=500)
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertEqual("ineligible", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_cfe_with_incomplete_property_data_is_unknown(self):
        _, _, cfe_result = self.checker_with_blank_property()._do_cfe_civil_check()
        self.assertEqual("not_yet_known", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_incomplete_income_data_is_unknown(self):
        _, _, cfe_result = self.checker_with_income_without_earnings(
            maintenance_received=100, child_benefits=500, tax_credits=None
        )._do_cfe_civil_check()
        self.assertEqual("not_yet_known", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_incomplete_deductions_data_is_unknown(self):
        _, _, cfe_result = self.checker_with_income_without_earnings(
            maintenance_received=100, child_benefits=500, deductions={}
        )._do_cfe_civil_check()
        self.assertEqual("not_yet_known", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_incomplete_self_employment_is_unknown(self):
        _, _, cfe_result = self.checker_with_income_without_earnings(
            maintenance_received=100, child_benefits=500, self_employed=True
        )._do_cfe_civil_check()
        self.assertEqual("not_yet_known", cfe_result.overall_result)

    def checker_without_savings(self):
        cd = fixtures.get_default_case_data()
        cd["you"].update({"savings": {}})

        case_data = CaseData(**cd)
        return EligibilityChecker(case_data=case_data)

    @test_vcr.use_vcr_cassette
    def test_cfe_with_no_savings_data_is_unknown(self):
        _, _, cfe_result = self.checker_without_savings()._do_cfe_civil_check()
        self.assertEqual("not_yet_known", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_under_60_with_capital(self):
        facts = dict(
            is_you_or_your_partner_over_60=False,
            is_you_under_18=False,
            has_partner=False,
            dependants_young=0,
            dependants_old=0,
        )
        checker = self.checker_with_assets(20000 * 100, facts)
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertEqual("ineligible", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_over_60_with_capital(self):
        facts = dict(
            is_you_or_your_partner_over_60=True,
            is_you_under_18=False,
            has_partner=False,
            dependants_young=0,
            dependants_old=0,
        )
        checker = self.checker_with_assets(20000 * 100, facts)
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_applicant_receives_qualifying_benefit(self):
        checker = self.checker_with_facts(dict(on_passported_benefits=True))
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertTrue(cfe_result.applicant_details()["receives_qualifying_benefit"])

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_applicant_receives_asylum_support(self):
        _, _, cfe_result = self.checker_with_facts(dict(on_nass_benefits=True))._do_cfe_civil_check()
        self.assertEqual("eligible", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_with_proceeding_types(self):
        _, _, cfe_result = self.checker_with_category(category="immigration")._do_cfe_civil_check()
        self.assertEqual("eligible", cfe_result.overall_result)

    @test_vcr.use_vcr_cassette
    def test_enough_deductions_creates_eligible_cfe_request(self):
        deductions = dict(
            income_tax=0,
            national_insurance=0,
            maintenance=454500,
            childcare=3737,
            mortgage=4242,
            rent=5757,
            criminal_legalaid_contributions=2424,
        )
        _, _, cfe_response = self.checker_with_deductions(
            income=2000 * 100, deductions=deductions
        )._do_cfe_civil_check()
        self.assertEqual("eligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_smod_capital_below_limit_is_ignored(self):
        checker = self.checker_with_disputed_assets(50000 * 100)
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_smod_capital_above_limit_is_not_ignored(self):
        checker = self.checker_with_disputed_assets(150000 * 100)
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("ineligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_translate_capital_data_merges_savings(self):
        checker = self.checker_with_disputed_assets(60000, savings=self.savings_dict(150000))
        expected = {
            "bank_accounts": [],
            "non_liquid_capital": [
                {
                    "description": "Valuable items worth over 500 pounds",
                    "subject_matter_of_dispute": False,
                    "value": 1500.0,
                },
                {
                    "description": "Valuable items worth over 500 pounds",
                    "subject_matter_of_dispute": True,
                    "value": 600.0,
                },
            ],
        }
        self.assertEqual(expected, checker._translate_capital_data(checker.case_data)["capitals"])

    @test_vcr.use_vcr_cassette
    def test_partner_without_savings_is_unknown(self):
        checker = self.checker_with_facts(facts=dict(has_partner=True), partner=dict())
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_assessment_attribute_not_aggregated_no_income_low_capital_for_under_18_no_income(self):
        checker = self.checker_with_facts(dict(under_18_passported=True, is_you_under_18=True))
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_assessment_attribute_not_aggregated_no_income_low_capital_for_under_18_low_income(self):
        checker = self.checker_with_facts_and_income(under_18_passported=True, is_you_under_18=True, income=10000)
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_assessment_attribute_not_aggregated_no_income_low_capital_for_under_18_high_income(self):
        checker = self.checker_with_facts_and_income(under_18_passported=True, is_you_under_18=True, income=2000000)
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("eligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_assessment_attribute_not_aggregated_no_income_low_capital_for_under_18_high_income_non_passported(self):
        checker = self.checker_with_facts_and_income(under_18_passported=False, is_you_under_18=True, income=2000000)
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("ineligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_assessment_attribute_not_aggregated_no_income_low_capital_for_over_18_low_income(self):
        checker = self.checker_with_facts_and_income(under_18_passported=False, is_you_under_18=False, income=10000)
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("not_yet_known", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_assessment_attribute_not_aggregated_no_income_low_capital_for_over_18_high_income(self):
        checker = self.checker_with_facts_and_income(under_18_passported=False, is_you_under_18=False, income=2000000)
        cfe_response = self.do_cfe_civil_check(checker)
        self.assertEqual("ineligible", cfe_response.overall_result)

    @test_vcr.use_vcr_cassette
    def test_cfe_request_without_dependants_young(self):
        checker = self.checker_with_facts_without_defaults(dict(on_passported_benefits=True))
        cfe_result = self.do_cfe_civil_check(checker)
        self.assertTrue(cfe_result.applicant_details()["receives_qualifying_benefit"])
