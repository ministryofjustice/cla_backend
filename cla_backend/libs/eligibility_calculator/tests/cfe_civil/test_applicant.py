from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.applicant import translate_applicant
from cla_backend.libs.eligibility_calculator.models import Facts


class TestTranslateApplicant(TestCase):
    def test_applicant_receives_qualifying_benefit_set_to_None_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_passported_benefits=None)
        output = translate_applicant(applicant_facts)
        expected = {
            "applicant": {
                "date_of_birth": "1992-07-25",
                "receives_qualifying_benefit": False,
                "receives_asylum_support": False
            }
        }
        self.assertEqual(expected, output)

    def test_applicant_receives_qualifying_benefit_set_to_False_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_passported_benefits=False)
        output = translate_applicant(applicant_facts)
        expected = {
            "applicant": {
                "date_of_birth": "1992-07-25",
                "receives_qualifying_benefit": False,
                "receives_asylum_support": False
            }
        }
        self.assertEqual(expected, output)

    def test_applicant_receives_qualifying_benefit_set_to_True_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_passported_benefits=True)
        output = translate_applicant(applicant_facts)
        expected = {
            "applicant": {
                "date_of_birth": "1992-07-25",
                "receives_qualifying_benefit": True,
                "receives_asylum_support": False
            }
        }
        self.assertEqual(expected, output)
