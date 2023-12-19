from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.savings import translate_savings
from cla_backend.libs.eligibility_calculator.models import Savings


class TestTranslateSavings(TestCase):
    def test_bank_balance_and_investments(self):
        savings = Savings(bank_balance=270010, investment_balance=100010, asset_balance=200000)
        output = translate_savings(savings)
        expected = {"capitals": {
            "bank_accounts": [
                {
                    "value": 2700.10,
                    "description": "Savings",
                    "subject_matter_of_dispute": False
                },
                {
                    "value": 1000.10,
                    "description": "Investment",
                    "subject_matter_of_dispute": False
                },
            ],
            "non_liquid_capital": [
                {
                    "value": 2000,
                    "description": "Valuable items worth over 500 pounds",
                    "subject_matter_of_dispute": False
                },

            ],
        }}
        self.assertEqual(expected, output)

    def test_assets(self):
        savings = Savings(bank_balance=0, investment_balance=0, asset_balance=80011)
        output = translate_savings(savings)
        expected = {"capitals": {
            "bank_accounts": [],
            "non_liquid_capital": [
                {
                    "value": 800.11,
                    "description": "Valuable items worth over 500 pounds",
                    "subject_matter_of_dispute": False
                },
            ]
        }}
        self.assertEqual(expected, output)

    def test_empty_savings_generates_empty_dict(self):
        savings = Savings()

        output = translate_savings(savings)

        expected = {}
        self.assertEqual(expected, output)
