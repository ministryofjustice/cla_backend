import datetime
from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.dependants import translate_dependants
from cla_backend.libs.eligibility_calculator.models import Facts


class TestTranslateDependants(TestCase):
    def test_no_dependants(self):
        today = datetime.date(2023, 11, 23)
        facts = Facts(dependants_old=0, dependants_young=0)

        output = translate_dependants(today, facts)
        expected = {"dependants": []}
        self.assertEqual(expected, output)

    def test_old_and_young_dependants(self):
        today = datetime.date(2023, 11, 23)
        facts = Facts(dependants_old=1, dependants_young=2)

        output = translate_dependants(today, facts)
        expected = {
            "dependants": [
                {
                    "date_of_birth": "2008-11-23",
                    "in_full_time_education": False,
                    "relationship": "child_relative",
                    "income": {"frequency": "weekly", "amount": 0},
                    "assets_value": 0,
                },
                {
                    "date_of_birth": "2008-11-23",
                    "in_full_time_education": False,
                    "relationship": "child_relative",
                    "income": {"frequency": "weekly", "amount": 0},
                    "assets_value": 0,
                },
                {
                    "date_of_birth": "2006-11-23",
                    "in_full_time_education": False,
                    "relationship": "adult_relative",
                    "income": {"frequency": "weekly", "amount": 0},
                    "assets_value": 0,
                },
            ]
        }
        self.assertEqual(expected, output)
