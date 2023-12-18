from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.applicant import translate_applicant
from cla_backend.libs.eligibility_calculator.models import Facts


class TestTranslateApplicant(TestCase):
    def test_applicant_receives_qualifying_benefit_set_to_None_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_passported_benefits=None)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_receives_qualifying_benefit_set_to_False_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_passported_benefits=False)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_receives_qualifying_benefit_set_to_True_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_passported_benefits=True)
        output = translate_applicant(applicant_facts)
        expected = {
            "receives_qualifying_benefit": True,
        }
        self.assertEqual(expected, output)

    def test_applicant_receives_asylum_support_set_to_None_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_nass_benefits=None)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_receives_asylum_support_set_to_False_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_nass_benefits=False)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_receives_asylum_support_set_to_True_produces_valid_cfe_request(self):
        applicant_facts = Facts(on_nass_benefits=True)
        output = translate_applicant(applicant_facts)
        expected = {
            "receives_asylum_support": True,
        }
        self.assertEqual(expected, output)
