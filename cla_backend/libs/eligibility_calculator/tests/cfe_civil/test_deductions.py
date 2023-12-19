from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.deductions import DeductionsTranslator
from cla_backend.libs.eligibility_calculator.models import Deductions


class TestTranslateDeductions(TestCase):
    def test_deductions_all_attributes_gives_outgoings(self):
        expected = {
            "regular_transactions": [
                {
                    "category": "maintenance_out",
                    "operation": "debit",
                    "frequency": "monthly",
                    "amount": 45.45
                },
                {
                    "category": "child_care",
                    "operation": "debit",
                    "frequency": "monthly",
                    "amount": 37.37
                },
                {
                    "category": "rent_or_mortgage",
                    "operation": "debit",
                    "frequency": "monthly",
                    "amount": 42.42
                },
                {
                    "category": "rent_or_mortgage",
                    "operation": "debit",
                    "frequency": "monthly",
                    "amount": 57.57
                },
                {
                    "category": "legal_aid",
                    "operation": "debit",
                    "frequency": "monthly",
                    "amount": 24.24
                }
            ],
        }
        deductions = Deductions(maintenance=4545, childcare=3737, mortgage=4242, rent=5757,
                                criminal_legalaid_contributions=2424)
        translator = DeductionsTranslator(deductions)

        self.assertTrue(translator.is_complete())
        # assert list equality w/o respect to ordering
        self.assertEqual(set(expected), set(translator.translate()))

    def test_missing_field_gives_no_outgoings(self):
        deductions = Deductions(maintenance=4545, childcare=3737, mortgage=4242, rent=5757)
        translator = DeductionsTranslator(deductions)
        self.assertFalse(translator.is_complete())
