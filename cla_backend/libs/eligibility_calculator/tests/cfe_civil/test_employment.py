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
                        "student_debt_repayment": 0
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
                        "student_debt_repayment": 0
                    }
                }
            ],
        }
        self.assertEqual(expected, output)
