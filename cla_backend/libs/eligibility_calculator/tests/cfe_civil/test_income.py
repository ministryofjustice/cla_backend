from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.income import translate_income
from cla_backend.libs.eligibility_calculator.models import Income


class TestTranslateIncome(TestCase):
    def test_fully_populated_income_produces_valid_cfe_request(self):
        income = Income(
            benefits=80000,
            tax_credits=100,
            child_benefits=200,
            maintenance_received=10000,
            pension=400,
            other_income=300,
        )

        output = translate_income(income)

        expected = {
            "regular_transactions": [
                {
                    "category": "benefits",
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": 800,
                },
                {
                    "category": "benefits",
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": 1.0,
                },
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
                    "amount": 2.0,
                },
                {
                    "category": "friends_or_family",
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": 3.0,
                },
                {
                    "category": "pension",
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": 4.0,
                },
            ]
        }
        self.maxDiff = None
        self.assertEqual(expected, output)

    def test_minimal_income_produces_single_cfe_value(self):
        income = Income(
            benefits=80000, tax_credits=0, child_benefits=0, maintenance_received=0, pension=0, other_income=0
        )

        output = translate_income(income)

        expected = {
            "regular_transactions": [
                {
                    "category": "benefits",
                    "operation": "credit",
                    "frequency": "monthly",
                    "amount": 800,
                }
            ],
        }
        self.assertEqual(expected, output)

    def test_zero_income_produces_empty_cfe_array(self):
        income = Income(benefits=0, tax_credits=0, child_benefits=0, maintenance_received=0, pension=0, other_income=0)
        output = translate_income(income)
        expected = {
            "regular_transactions": [],
        }
        self.assertEqual(expected, output)
