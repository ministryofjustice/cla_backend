from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.deductions import translate_deductions
from cla_backend.libs.eligibility_calculator.models import Deductions


class TestTranslateDeductions(TestCase):
    def test_deductions_all_attributes_gives_outgoings(self):
        expected = {
            "regular_transactions": [
                {"category": "maintenance_out", "operation": "debit", "frequency": "monthly", "amount": 45.45},
                {"category": "child_care", "operation": "debit", "frequency": "monthly", "amount": 37.37},
                {"category": "rent_or_mortgage", "operation": "debit", "frequency": "monthly", "amount": 42.42},
                {"category": "rent_or_mortgage", "operation": "debit", "frequency": "monthly", "amount": 57.57},
                {"category": "legal_aid", "operation": "debit", "frequency": "monthly", "amount": 24.24},
            ],
        }
        deductions = Deductions(
            maintenance=4545, childcare=3737, mortgage=4242, rent=5757, criminal_legalaid_contributions=2424
        )
        # assert list equality w/o respect to ordering
        self.assertEqual(set(expected), set(translate_deductions(deductions)))

    def test_missing_field(self):
        expected = {
            "regular_transactions": [
                {"amount": 45.45, "category": "maintenance_out", "frequency": "monthly", "operation": "debit"}
            ]
        }
        deductions = Deductions(maintenance=4545)
        self.assertEqual(expected, translate_deductions(deductions))

    def test_some_fields_zero(self):
        expected = {
            "regular_transactions": [
                {"category": "rent_or_mortgage", "operation": "debit", "frequency": "monthly", "amount": 42.42}
            ],
        }
        deductions = Deductions(maintenance=0, childcare=0, mortgage=0, rent=4242, criminal_legalaid_contributions=0)
        self.assertEqual(expected, translate_deductions(deductions))
