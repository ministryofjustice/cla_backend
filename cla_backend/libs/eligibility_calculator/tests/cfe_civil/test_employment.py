from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.employment import translate_employment
from cla_backend.libs.eligibility_calculator.models import Income, Deductions


class TestCfeIncome(TestCase):
    def test_no_earnings_returns_no_employments(self):
        income = Income(earnings=0, self_employed=False)
        deductions = Deductions(income_tax=0, national_insurance=0)
        output = translate_employment(income, deductions)
        expected = {
            "employment_details": [],
        }
        self.assertEqual(expected, output)

    def test_employment_returns_employment_details(self):
        income = Income(earnings=250000, self_employed=False)
        deductions = Deductions(income_tax=40000, national_insurance=6500)
        output = translate_employment(income, deductions)
        expected = {
            "employment_details": [
                {
                    "income": {
                        "receiving_only_statutory_sick_or_maternity_pay": False,
                        "frequency": "monthly",
                        "gross": 2500,
                        "benefits_in_kind": 0,
                        "tax": -400,
                        "national_insurance": -65,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0,
                    }
                }
            ],
        }
        self.assertEqual(expected, output)

    def test_self_employment(self):
        income = Income(earnings=250000, self_employed=True)
        deductions = Deductions(income_tax=40000, national_insurance=6500)
        output = translate_employment(income, deductions)
        expected = {
            "self_employment_details": [
                {
                    "income": {
                        "frequency": "monthly",
                        "gross": 2500,
                        "tax": -400,
                        "national_insurance": -65,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0,
                    }
                }
            ],
        }
        self.assertEqual(expected, output)

    def test_self_employment_drawings(self):
        income = Income(earnings=0, self_employed=True, self_employment_drawings=20000)
        deductions = Deductions(income_tax=0, national_insurance=0)
        output = translate_employment(income, deductions)
        expected = {
            "self_employment_details": [
                {
                    "income": {
                        "frequency": "monthly",
                        "gross": 200,
                        "tax": 0,
                        "national_insurance": 0,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0,
                    }
                }
            ],
        }
        self.assertEqual(expected, output)

    def test_self_employment_earnings_and_drawings(self):
        income = Income(earnings=10000, self_employed=True, self_employment_drawings=20000)
        deductions = Deductions(income_tax=0, national_insurance=0)
        output = translate_employment(income, deductions)
        expected = {
            "self_employment_details": [
                {
                    "income": {
                        "frequency": "monthly",
                        "gross": 300,
                        "tax": 0,
                        "national_insurance": 0,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0,
                    }
                }
            ],
        }
        self.assertEqual(expected, output)

    def test_no_keys(self):
        income = Income()
        deductions = Deductions()
        output = translate_employment(income, deductions)
        expected = {"employment_details": []}
        self.assertEqual(expected, output)

    def test_missing_income_tax(self):
        income = Income()
        deductions = Deductions(national_insurance=1)
        output = translate_employment(income, deductions)
        expected = {
            "employment_details": [
                {
                    "income": {
                        "benefits_in_kind": 0,
                        "frequency": "monthly",
                        "gross": 0,
                        "national_insurance": -0.01,
                        "prisoner_levy": 0,
                        "receiving_only_statutory_sick_or_maternity_pay": False,
                        "student_debt_repayment": 0,
                        "tax": 0,
                    }
                }
            ]
        }
        self.assertEqual(expected, output)

    def test_missing_national_insurance(self):
        income = Income()
        deductions = Deductions(income_tax=1)
        output = translate_employment(income, deductions)
        expected = {
            "employment_details": [
                {
                    "income": {
                        "benefits_in_kind": 0,
                        "frequency": "monthly",
                        "gross": 0,
                        "national_insurance": 0,
                        "prisoner_levy": 0,
                        "receiving_only_statutory_sick_or_maternity_pay": False,
                        "student_debt_repayment": 0,
                        "tax": -0.01,
                    }
                }
            ]
        }
        self.assertEqual(expected, output)
