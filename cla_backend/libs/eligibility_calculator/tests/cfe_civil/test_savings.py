from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.savings import translate_savings
from cla_backend.libs.eligibility_calculator.models import Savings


class TestTranslateSavings(TestCase):
    def test_bank_balance_and_investments(self):
        savings = Savings(bank_balance=270000, investment_balance=100000, asset_balance=0)
        output = translate_savings(savings)
        expected = {"capitals": {
            "bank_accounts": [
                {
                    "value": 2700,
                    "description": "Savings Account",
                    "subject_matter_of_dispute": False
                },
                {
                    "value": 1000,
                    "description": "Investment",
                    "subject_matter_of_dispute": False
                },
            ],
            "non_liquid_capital": [],
        }}
        self.assertEqual(expected, output)

    def test_assets(self):
        savings = Savings(bank_balance=0, investment_balance=0, asset_balance=80000)
        output = translate_savings(savings)
        expected = {"capitals": {
            "bank_accounts": [],
            "non_liquid_capital": [
                {
                    "value": 800,
                    "description": "Asset",
                    "subject_matter_of_dispute": False
                },
            ]
        }}
        self.assertEqual(expected, output)
