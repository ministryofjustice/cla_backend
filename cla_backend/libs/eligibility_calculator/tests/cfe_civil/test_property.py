from unittest import TestCase

from cla_backend.libs.eligibility_calculator.cfe_civil.property import translate_property


class TestTranslateProperty(TestCase):
    def test_multiple_properties(self):
        houses = [
            {"disputed": False, "main": True, "share": 80, "value": 100000 * 100, "mortgage_left": 50000 * 100},
            {"disputed": False, "main": False, "share": 50, "value": 500000 * 100, "mortgage_left": 200000 * 100},
        ]

        output = translate_property(houses)
        expected = {
            "properties": {
                "main_home": {
                    "value": 100000,
                    "outstanding_mortgage": 50000,
                    "percentage_owned": 80,
                    "shared_with_housing_assoc": False,
                    "subject_matter_of_dispute": False,
                },
                "additional_properties": [
                    {
                        "value": 500000,
                        "outstanding_mortgage": 200000,
                        "percentage_owned": 50,
                        "shared_with_housing_assoc": False,
                        "subject_matter_of_dispute": False,
                    }
                ],
            }
        }
        self.assertEqual(expected, output)

    def test_properties_no_main_home(self):
        houses = [{"disputed": True, "main": False, "share": 50, "value": 500000 * 100, "mortgage_left": 200000 * 100}]

        output = translate_property(houses)
        expected = {
            "properties": {
                "additional_properties": [
                    {
                        "value": 500000,
                        "outstanding_mortgage": 200000,
                        "percentage_owned": 50,
                        "shared_with_housing_assoc": False,
                        "subject_matter_of_dispute": True,
                    }
                ]
            }
        }
        self.assertEqual(expected, output)

    def test_invalid_property_returns_no_results(self):
        houses = [{}]
        self.assertEqual({}, translate_property(houses))

    def test_properties_two_main_homes(self):
        houses = [
            {"disputed": True, "main": True, "share": 50, "value": 500000 * 100, "mortgage_left": 200000 * 100},
            {"disputed": False, "main": True, "share": 40, "value": 400000 * 100, "mortgage_left": 100000 * 100},
        ]

        output = translate_property(houses)
        expected = {
            "properties": {
                "main_home": {
                    "value": 500000,
                    "outstanding_mortgage": 200000,
                    "percentage_owned": 50,
                    "shared_with_housing_assoc": False,
                    "subject_matter_of_dispute": True,
                },
                "additional_properties": [
                    {
                        "value": 400000,
                        "outstanding_mortgage": 100000,
                        "percentage_owned": 40,
                        "shared_with_housing_assoc": False,
                        "subject_matter_of_dispute": False,
                    }
                ],
            }
        }
        self.assertEqual(expected, output)
