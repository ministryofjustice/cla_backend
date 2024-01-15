from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.applicant import translate_applicant
from cla_backend.libs.eligibility_calculator.models import Facts


class TestOneBenefitKnown(TestCase):
    def test_applicant_on_passported_benefits_None(self):
        applicant_facts = Facts(on_passported_benefits=None)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_on_passported_benefits_False(self):
        applicant_facts = Facts(on_passported_benefits=False)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_on_passported_benefits_True(self):
        applicant_facts = Facts(on_passported_benefits=True)
        output = translate_applicant(applicant_facts)
        expected = {
            "receives_qualifying_benefit": True,
        }
        self.assertEqual(expected, output)

    def test_applicant_on_nass_benefits_None(self):
        applicant_facts = Facts(on_nass_benefits=None)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_on_nass_benefits_False(self):
        applicant_facts = Facts(on_nass_benefits=False)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)

    def test_applicant_on_nass_benefits_True(self):
        applicant_facts = Facts(on_nass_benefits=True)
        output = translate_applicant(applicant_facts)
        expected = {
            "receives_asylum_support": True,
        }
        self.assertEqual(expected, output)


class TestBothBenefitsKnown(TestCase):
    def test_on_both_benefits(self):
        applicant_facts = Facts(on_passported_benefits=True, on_nass_benefits=True)
        output = translate_applicant(applicant_facts)
        expected = {
            "receives_qualifying_benefit": True,
            "receives_asylum_support": True,
        }
        self.assertEqual(expected, output)

    def test_on_passported_benefit_only(self):
        applicant_facts = Facts(on_passported_benefits=True, on_nass_benefits=False)
        output = translate_applicant(applicant_facts)
        expected = {
            "receives_qualifying_benefit": True,
        }
        self.assertEqual(expected, output)

    def test_on_nass_only(self):
        applicant_facts = Facts(on_passported_benefits=False, on_nass_benefits=True)
        output = translate_applicant(applicant_facts)
        expected = {
            "receives_asylum_support": True,
        }
        self.assertEqual(expected, output)

    def test_on_neither_benefit(self):
        applicant_facts = Facts(on_passported_benefits=False, on_nass_benefits=False)
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)


class TestNeitherBenefitKnown(TestCase):
    def test_neither_set(self):
        applicant_facts = Facts()
        output = translate_applicant(applicant_facts)
        self.assertEqual({}, output)
