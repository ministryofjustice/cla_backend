from unittest import TestCase
from cla_backend.libs.eligibility_calculator.cfe_civil.under_18_passported import translate_under_18_passported
from cla_backend.libs.eligibility_calculator.models import Facts


class TestUnder18Passported(TestCase):
    def test_assessment_not_aggregated_no_income_low_capital_for_under_18(self):
        applicant_facts = Facts(under_18_passported=True, is_you_under_18=True)
        output = translate_under_18_passported(applicant_facts)
        expected = {
            "not_aggregated_no_income_low_capital": True,
        }
        self.assertEqual(expected, output)

    def test_assessment_not_aggregated_no_income_low_capital_for_over_18(self):
        applicant_facts = Facts(under_18_passported=False, is_you_under_18=False)
        output = translate_under_18_passported(applicant_facts)
        expected = {}
        self.assertEqual(expected, output)

    def test_assessment_not_aggregated_no_income_low_capital_for_attribute_is_you_under_18_set_to_false(self):
        applicant_facts = Facts(under_18_passported=True, is_you_under_18=False)
        output = translate_under_18_passported(applicant_facts)
        expected = {}
        self.assertEqual(expected, output)

    def test_assessment_not_aggregated_no_income_low_capital_for_attribute_under_18_passported_set_to_false(self):
        applicant_facts = Facts(under_18_passported=False, is_you_under_18=True)
        output = translate_under_18_passported(applicant_facts)
        expected = {}
        self.assertEqual(expected, output)
