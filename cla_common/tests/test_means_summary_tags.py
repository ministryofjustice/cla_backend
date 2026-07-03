import unittest

from ..templatetags.means_summary_tags import MeansSummaryFormatter


class MeansSummaryFormatterTestCase(unittest.TestCase):
    """
        Intentionally not unit testing completely as it's likely going to change
        quite a lot.
        Unit testing the core parts though.
    """

    def setUp(self):
        super(MeansSummaryFormatterTestCase, self).setUp()
        self.formatter = MeansSummaryFormatter()

    # YOUR DETAILS

    def test_your_details_None(self):
        section = self.formatter.get_your_details(None)
        self.assertEqual(section, None)

    def test_your_details_complete(self):
        data = {
            "category": "my-category",
            "your_problem_notes": "my-notes",
            "has_partner": True,
            "on_passported_benefits": True,
            "has_children": True,
            "is_you_or_your_partner_over_60": True,
        }

        section = self.formatter.get_your_details(data)
        self.assertEqual(section["header"], "Details you've already given")
        self.assertEqual(section["step"], "your_problem")
        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "You are looking for help about my-category",
                "Additional details about your problem: my-notes",
                "You live with a partner",
                "You or your partner are on Income Support benefits",
                "You have children dependent on you",
                "You or your partner are 60 or over",
            ],
        )

    def test_your_details_minimal(self):
        data = {"category": "my-category"}

        section = self.formatter.get_your_details(data)
        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "You are looking for help about my-category",
                "You don't live with a partner",
                "You or your partner are not on Income Support benefits",
                "You don't have children dependent on you",
                "You or your partner are not 60 or over",
            ],
        )

    # YOUR FINANCES

    def test_get_your_finances_None(self):
        section = self.formatter.get_your_finances(None)
        self.assertEqual(section, None)

    def test_get_your_finances_complete(self):
        data = {
            "property_set": [
                {"value": 100000, "mortgage_left": 100, "share": 30, "disputed": True},
                {"value": 200000, "mortgage_left": 0, "share": 20, "disputed": False},
            ],
            "you": {
                "savings": {
                    "bank_balance": 111,
                    "investment_balance": 222,
                    "asset_balance": 333,
                    "credit_balance": 444,
                }
            },
            "partner": {
                "savings": {
                    "bank_balance": 555,
                    "investment_balance": 666,
                    "asset_balance": 777,
                    "credit_balance": 888,
                }
            },
        }

        section = self.formatter.get_your_finances(data)
        self.assertEqual(section["header"], "Your finances")
        self.assertEqual(section["step"], "your_capital")
        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "You have 2 properties",
                "Property 1: Your property is worth &pound1000.00",
                "Property 1: You have &pound;1.00 left to pay on the mortgage",
                "Property 1: You own 30% of the property",
                "Property 1: This is a disputed property",
                "Property 2: Your property is worth &pound2000.00",
                "Property 2: You have no outstanding mortgage on the property",
                "Property 2: You own 20% of the property",
                "Property 2: This is not a disputed property",
                "You have &pound;1.11 saved in a bank or building society",
                "You have &pound;2.22 in investments, shares, ISAs",
                "You have valuable items worth &pound;3.33",
                "You have &pound;4.44 owned to you",
                "Your partner has &pound;5.55 saved in a bank or building society",
                "Your partner has &pound;6.66 in investments, shares, ISAs",
                "Your partner has valuable items worth &pound;7.77",
                "Your partner has &pound;8.88 owned to them",
            ],
        )

    def test_get_your_finances_minimal(self):
        data = {"you": {"savings": {"bank_balance": 0}}, "partner": {"savings": {"bank_balance": 0}}}

        section = self.formatter.get_your_finances(data)
        self.assertEqual(section["header"], "Your finances")
        self.assertEqual(section["step"], "your_capital")
        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "You don't have any money saved in a bank or building society",
                "You don't have any money in investments, shares, ISAs",
                "You don't have any valuable items",
                "You don't have any money owned to you",
                "Your partner doesn't have any money saved in a bank or building society",
                "Your partner doesn't have any money in investments, shares, ISAs",
                "Your partner doesn't have any valuable items",
                "Your partner doesn't have any money owned to them",
            ],
        )

    # YOUR INCOME

    def test_get_your_income_None(self):
        section = self.formatter.get_your_income(None)
        self.assertEqual(section, None)

    def test_get_your_income_complete(self):
        data = {
            "you": {
                "income": {
                    "earnings": {"interval_period": u"per_month", "per_interval_value": 111},
                    "self_employed": True,
                    "other_income": {"interval_period": u"per_month", "per_interval_value": 222},
                }
            },
            "partner": {
                "income": {
                    "earnings": {"interval_period": u"per_month", "per_interval_value": 333},
                    "self_employed": False,
                    "other_income": {"interval_period": u"per_month", "per_interval_value": 444},
                }
            },
            "dependants_young": 1,
            "dependants_old": 9,
        }

        section = self.formatter.get_your_income(data)
        self.assertEqual(section["header"], "Your income")
        self.assertEqual(section["step"], "your_income")
        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "Your earnings: &pound;1.11 per month",
                "You are self employed",
                "Your other income: &pound;2.22 per month",
                "Your partner's earnings: &pound;3.33 per month",
                "Your partner is not self employed",
                "Your partner's other income: &pound;4.44 per month",
                "You have one child aged 15 and under",
                "You have 9 children aged 16 and over",
            ],
        )

    def test_get_your_income_minimal(self):
        data = {
            "you": {"income": {"earnings": {"interval_period": u"per_month", "per_interval_value": 0}}},
            "partner": {"income": {"earnings": {"interval_period": u"per_month", "per_interval_value": 0}}},
        }

        section = self.formatter.get_your_income(data)
        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "You don't have earnings",
                "You are not self employed",
                "You don't have any other income",
                "Your partner doesn't have earnings",
                "Your partner is not self employed",
                "Your partner doesn't have any other income",
            ],
        )

    # YOUR ALLOWANCES

    def test_get_your_allowances_None(self):
        section = self.formatter.get_your_allowances(None)
        self.assertEqual(section, None)

    def test_get_your_allowances_complete(self):
        data = {
            "you": {
                "deductions": {
                    "mortgage": {"per_interval_value": 110, "interval_period": "per_month"},
                    "rent": {"per_interval_value": 1, "interval_period": "per_month"},
                    "income_tax": {"per_interval_value": 202, "interval_period": "per_month"},
                    "national_insurance": {"per_interval_value": 20, "interval_period": "per_month"},
                    "maintenance": {"per_interval_value": 333, "interval_period": "per_month"},
                    "childcare": {"per_interval_value": 444, "interval_period": "per_month"},
                    "criminal_legalaid_contributions": 555,
                }
            },
            "partner": {
                "deductions": {
                    "mortgage": {"per_interval_value": 333, "interval_period": "per_month"},
                    "rent": {"per_interval_value": 333, "interval_period": "per_month"},
                    "income_tax": {"per_interval_value": 666, "interval_period": "per_month"},
                    "national_insurance": {"per_interval_value": 111, "interval_period": "per_month"},
                    "maintenance": {"per_interval_value": 888, "interval_period": "per_month"},
                    "childcare": {"per_interval_value": 999, "interval_period": "per_month"},
                    "criminal_legalaid_contributions": 987,
                }
            },
        }

        section = self.formatter.get_your_allowances(data)
        self.assertEqual(section["header"], "Your expenses")
        self.assertEqual(section["step"], "your_allowances")

        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "Your mortgage: &pound;1.10 per month",
                "Your rent: &pound;0.01 per month",
                "Your national insurance: &pound;0.20 per month",
                "Your income tax: &pound;2.02 per month",
                "Your maintenance: &pound;3.33 per month",
                "Your childcare: &pound;4.44 per month",
                "Your payments being made towards a contribution order: &pound;5.55",
                "Your partner's mortgage: &pound;3.33 per month",
                "Your partner's rent: &pound;3.33 per month",
                "Your partner's national insurance: &pound;1.11 per month",
                "Your partner's income tax: &pound;6.66 per month",
                "Your partner's maintenance: &pound;8.88 per month",
                "Your partner's childcare: &pound;9.99 per month",
                "Your partner's payments being made towards a contribution order: &pound;9.87",
            ],
        )

    def test_get_your_allowances_minimal(self):
        data = {
            "you": {
                "deductions": {
                    "mortgage": {"per_interval_value": 0, "interval_period": "per_month"},
                    "rent": {"per_interval_value": 0, "interval_period": "per_month"},
                    "income_tax": {"per_interval_value": 0, "interval_period": "per_month"},
                    "national_insurance": {"per_interval_value": 0, "interval_period": "per_month"},
                    "maintenance": {"per_interval_value": 0, "interval_period": "per_month"},
                    "childcare": {"per_interval_value": 0, "interval_period": "per_month"},
                    "criminal_legalaid_contributions": 0,
                }
            }
        }

        section = self.formatter.get_your_allowances(data)
        self.assertEqual(
            [unicode(s) for s in section["items"]],
            [
                "Your mortgage: &pound;0.00 per month",
                "Your rent: &pound;0.00 per month",
                "Your national insurance: &pound;0.00 per month",
                "Your income tax: &pound;0.00 per month",
                "Your maintenance: &pound;0.00 per month",
                "Your childcare: &pound;0.00 per month",
                "Your payments being made towards a contribution order: &pound;0.00",
            ],
        )
