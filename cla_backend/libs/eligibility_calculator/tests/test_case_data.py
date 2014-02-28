import unittest
from ..models import CaseData
from ..exceptions import PropertyExpectedException
from .fixtures import case_data_dict

class TestCaseData(unittest.TestCase):

    GROSS_INCOME_FIELDS = [
        'earnings',
        'other_income',
    ]

    def setUp(self):
        self.default_case_data_dict = case_data_dict.copy()

    def test_total_income_calculation(self):
        cd = CaseData(**self.default_case_data_dict)
        ti = cd.total_income()
        gross_income_orig = sum(self.default_case_data_dict.get(f, 0) for f in self.GROSS_INCOME_FIELDS)
        self.assertEqual(gross_income_orig, ti)

    def test_bad_property_set_exception(self):
        cdd = self.default_case_data_dict.copy()
        cdd['foo'] = 'bar'
        with self.assertRaises(PropertyExpectedException):
            cd = CaseData(**cdd)
