import datetime
from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.age import translate_age
from cla_backend.libs.eligibility_calculator.models import Facts


class TestTranslateAge(TestCase):
    def test_over_60(self):
        today = datetime.date(2023, 11, 7)
        facts = Facts(is_you_or_your_partner_over_60=True, is_you_under_18=False)
        output = translate_age(today, facts)
        expected = {"date_of_birth": "1953-11-07"}
        self.assertEqual(expected, output)

    def test_under_60(self):
        today = datetime.date(2023, 11, 7)
        facts = Facts(is_you_or_your_partner_over_60=False, is_you_under_18=False)
        output = translate_age(today, facts)
        expected = {"date_of_birth": "1973-11-07"}
        self.assertEqual(expected, output)

    def test_under_18(self):
        today = datetime.date(2023, 11, 7)
        facts = Facts(is_you_or_your_partner_over_60=False, is_you_under_18=True)
        output = translate_age(today, facts)
        expected = {"date_of_birth": "2006-11-07"}
        self.assertEqual(expected, output)
