from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.income import translate_income
from cla_backend.libs.eligibility_calculator.models import Income


class TestTranslateIncome(TestCase):
    def test_assets(self):
        income = Income(earnings=0, self_employment_drawings=0, benefits=80000, tax_credits=0, child_benefits=0,
                        maintenance_received=10000, pension=0, other_income=0, self_employed=True)
        output = translate_income(income)
        expected = {
            "regular_transactions": [
                {
                    "category": "maintenance_in",
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": 100,
                },
                {
                    "category": "benefits",
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": 800,
                }
            ],
        }
        self.assertEqual(expected, output)
