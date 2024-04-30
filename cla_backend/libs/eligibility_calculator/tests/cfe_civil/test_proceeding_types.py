from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.proceeding_types import translate_proceeding_types
from cla_backend.libs.eligibility_calculator.models import CaseData


class TestProceedingTypes(TestCase):
    def test_category_with_None(self):
        case_data = CaseData(category=None)
        output = translate_proceeding_types(case_data.category)
        expected = [{"ccms_code": "SE013", "client_involvement_type": "A"}]
        self.assertEqual(expected, output)

    def test_category_without_immigration(self):
        case_data = CaseData(category="family")
        output = translate_proceeding_types(case_data.category)
        expected = [{"ccms_code": "SE013", "client_involvement_type": "A"}]
        self.assertEqual(expected, output)

    def test_category_with_immigration(self):
        case_data = CaseData(category="immigration")
        output = translate_proceeding_types(case_data.category)
        expected = [{"ccms_code": "IM030", "client_involvement_type": "A"}]
        self.assertEqual(expected, output)
