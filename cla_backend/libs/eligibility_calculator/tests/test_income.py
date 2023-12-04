from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.income import translate_income
from cla_backend.libs.eligibility_calculator.models import Income, Deductions

class TestCfeIncome(TestCase):
    def test_employment(self):
        income = Income(earnings=2500, self_employed=False)
        deductions = Deductions(income_tax=400, national_insurance=65)
        output = translate_income(income, deductions)
        expected = {
            "employment_details": [
                {
                    "income": {
                        "receiving_only_statutory_sick_or_maternity_pay": False,
                        "frequency": "monthly",
                        "gross": 2500,
                        "benefits_in_kind": 0,
                        "tax": 400,
                        "national_insurance": 65,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0
                    }
                }
            ],
        }
        self.assertEqual(expected, output)

    def test_self_employment(self):
        income = Income(earnings=2500, self_employed=True)
        deductions = Deductions(income_tax=400, national_insurance=65)
        output = translate_income(income, deductions)
        expected = {
            "self_employment_details": [
                {
                    "income": {
                        "receiving_only_statutory_sick_or_maternity_pay": False,
                        "frequency": "monthly",
                        "gross": 2500,
                        "benefits_in_kind": 0,
                        "tax": 400,
                        "national_insurance": 65,
                        "prisoner_levy": 0,
                        "student_debt_repayment": 0
                    }
                }
            ],
        }
        self.assertEqual(expected, output)
