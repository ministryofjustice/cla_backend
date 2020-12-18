# coding=utf-8
import random
import unittest

import mock
from . import fixtures
from .. import constants
from ..calculator import EligibilityChecker, CapitalCalculator
from ..exceptions import PropertyExpectedException
from ..models import CaseData, Facts


class MortgageCapRemovalMixin(object):
    def setUp(self):
        super(MortgageCapRemovalMixin, self).setUp()
        if CapitalCalculator.is_post_mortgage_cap_removal():
            self.expected_results_key = "post_mortgage_cap_removal"
        else:
            self.expected_results_key = "pre_mortgage_cap_removal"


class TestCapitalCalculator(MortgageCapRemovalMixin, unittest.TestCase):
    def _assert_calculations(self, expected_results, capital_calculator, capital):
        self.assertEqual(capital, expected_results["capital"])
        if "main_property_equity" in expected_results:
            self.assertEqual(capital_calculator.main_property["equity"], expected_results["main_property_equity"])
        if "other_properties_equity" in expected_results:
            self.assertEqual(
                capital_calculator.other_properties[0]["equity"], expected_results["other_properties_equity"]
            )

        self.assertDictEqual(capital_calculator.calcs, expected_results["calcs"])

    def test_incomplete_property_raises_exception(self):
        for i in range(5):
            prop = [24000000, 8000000, 100, True, True]
            prop[i] = None
            self.assertRaises(PropertyExpectedException, CapitalCalculator, properties=[self.make_property(*prop)])

    def test_empty_properties_dont_count(self):
        calc = CapitalCalculator(
            properties=[
                self.make_property(24000000, 8000000, 50, True, True),
                self.make_property(None, None, None, None, None),
                self.make_property(32000000, 24000000, 50, False, False),
            ]
        )
        self.assertEqual(len(calc.properties), 2)

    def test_without_properties(self):
        # default params
        calc = CapitalCalculator()
        self.assertEqual(calc.calculate_capital(), 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 0})

        # None param
        calc = CapitalCalculator(properties=None, non_disputed_liquid_capital=0)
        self.assertEqual(calc.calculate_capital(), 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 0})

        # liquid capital > 0
        calc = CapitalCalculator(non_disputed_liquid_capital=22)
        self.assertEqual(calc.calculate_capital(), 22)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 22})

    def make_property(self, value, mortgage_left, share, disputed, main):
        return {"value": value, "mortgage_left": mortgage_left, "share": share, "disputed": disputed, "main": main}

    def test_scenario_smod_1(self):
        # The applicant has a home worth £320,000 and the mortgage is £150,000.
        # The property is registered in joint names with his opponent.

        calc = CapitalCalculator(properties=[self.make_property(32000000, 15000000, 50, True, True)])
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertEqual(calc.main_property["equity"], 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0], "property_capital": 0, "liquid_capital": 0})

    def test_scenario_smod_2(self):
        # The applicant has a home worth £520,000 and the mortgage is £150,000.
        # The property is registered in his sole name.
        calc = CapitalCalculator(properties=[self.make_property(52000000, 15000000, 100, True, True)])
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 22000000,
                "main_property_equity": 22000000,
                "calcs": {"property_equities": [22000000], "property_capital": 22000000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 17000000,
                "main_property_equity": 17000000,
                "calcs": {"property_equities": [17000000], "property_capital": 17000000, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_scenario_smod_3(self):
        # The applicant’s main home is worth £240,000 and her other property is worth £90,000,
        # both properties are registered in joint names with her opponent and
        # both have mortgages of £80,000.

        calc = CapitalCalculator(
            properties=[
                self.make_property(24000000, 8000000, 50, True, True),
                self.make_property(9000000, 8000000, 50, True, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 500000,
                "main_property_equity": 0,
                "other_properties_equity": 500000,
                "calcs": {"property_equities": [0, 500000], "property_capital": 500000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 0,
                "main_property_equity": 0,
                "other_properties_equity": 0,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0},
            },
        }

        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_scenario_smod_4(self):
        # The applicant’s main home is worth £240,000 and her other property is worth £90,000,
        # both properties are registered in joint names with her opponent and
        # both have mortgages of £80,000.
        # only the other property is disputed

        calc = CapitalCalculator(
            properties=[
                self.make_property(24000000, 8000000, 50, False, True),
                self.make_property(9000000, 8000000, 50, True, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 1000000,
                "main_property_equity": 1000000,
                "calcs": {"property_equities": [1000000, 0], "property_capital": 1000000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 0,
                "main_property_equity": 0,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_scenario_no_smod_1(self):
        # The applicant has a home worth £150,000 and the mortgage is £75,000
        calc = CapitalCalculator(properties=[self.make_property(15000000, 7500000, 100, False, True)])
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertEqual(calc.main_property["equity"], 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0], "property_capital": 0, "liquid_capital": 0})

    def test_scenario_no_smod_2(self):
        # The applicant has a home worth £215,000 and the mortgage is £200,000
        calc = CapitalCalculator(properties=[self.make_property(21500000, 20000000, 100, False, True)])
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 1500000,
                "main_property_equity": 1500000,
                "calcs": {"property_equities": [1500000], "property_capital": 1500000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 0,
                "main_property_equity": 0,
                "calcs": {"property_equities": [0], "property_capital": 0, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_scenario_no_smod_3(self):
        # The client has a main dwelling worth £150,000 and a second dwelling worth £100,000.
        # Each has a mortgage of £80,000.
        calc = CapitalCalculator(
            properties=[
                self.make_property(15000000, 8000000, 100, False, True),
                self.make_property(10000000, 8000000, 100, False, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 5000000,
                "main_property_equity": 3000000,
                "other_property_equity": 2000000,
                "calcs": {"property_equities": [3000000, 2000000], "property_capital": 5000000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 2000000,
                "main_property_equity": 0,
                "other_property_equity": 2000000,
                "calcs": {"property_equities": [0, 2000000], "property_capital": 2000000, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_A12(self):
        # Testing if equity disregard applied to first property only
        calc = CapitalCalculator(
            properties=[
                self.make_property(5000000, 0, 100, False, True),
                self.make_property(4000000, 0, 100, False, False),
            ]
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 4000000)
        self.assertDictEqual(
            calc.calcs, {"property_equities": [0, 4000000], "property_capital": 4000000, "liquid_capital": 0}
        )

    def test_laa_scenario_A13(self):
        # Testing if equity disregard capped
        calc = CapitalCalculator(properties=[self.make_property(10800100, 0, 100, False, True)])
        capital = calc.calculate_capital()

        self.assertEqual(capital, 800100)
        self.assertDictEqual(
            calc.calcs, {"property_equities": [800100], "property_capital": 800100, "liquid_capital": 0}
        )

    def test_laa_scenario_A14(self):
        # Testing if mortgage disregard capped on second property
        calc = CapitalCalculator(
            properties=[
                self.make_property(10000000, 0, 100, False, True),
                self.make_property(10800100, 10000100, 100, False, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 800100,
                "calcs": {"property_equities": [0, 800100], "property_capital": 800100, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 800000,
                "calcs": {"property_equities": [0, 800000], "property_capital": 800000, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_A15(self):
        # Testing if mortgage disregard capped on first property
        calc = CapitalCalculator(properties=[self.make_property(20800100, 10000100, 100, False, True)])
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 800100,
                "calcs": {"property_equities": [800100], "property_capital": 800100, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 800000,
                "calcs": {"property_equities": [800000], "property_capital": 800000, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_A16(self):
        # Testing if mortgage disregard capped across all properties
        calc = CapitalCalculator(
            properties=[
                self.make_property(15000000, 5000000, 100, False, True),
                self.make_property(7500000, 7500000, 100, False, False),
            ],
            non_disputed_liquid_capital=800000,
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 3300000,
                "calcs": {"property_equities": [2500000, 0], "property_capital": 2500000, "liquid_capital": 800000},
            },
            "post_mortgage_cap_removal": {
                "capital": 800000,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 800000},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_A17(self):
        # Testing if mortgage disregard applied to second property before first
        calc = CapitalCalculator(
            properties=[
                self.make_property(10000000, 6000000, 100, False, True),
                self.make_property(5000000, 5000000, 100, False, False),
            ]
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0})

    def test_laa_scenario_smod_1(self):
        # Client - 1 Property
        # MV £180,000, Mortgage £10,000, SMOD, Equity Disregard
        # Capital £0.00 Pass

        calc = CapitalCalculator(properties=[self.make_property(18000000, 1000000, 100, True, True)])
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0], "property_capital": 0, "liquid_capital": 0})

    def test_laa_scenario_smod_2(self):
        # Client - 1 Property
        # MV £300,000, Mortgage £34,560, SMOD, Equity Disregard
        # Capital £65,440 Fail

        calc = CapitalCalculator(properties=[self.make_property(30000000, 3456000, 100, True, True)])
        capital = calc.calculate_capital()

        self.assertEqual(capital, 6544000)
        self.assertDictEqual(
            calc.calcs, {"property_equities": [6544000], "property_capital": 6544000, "liquid_capital": 0}
        )

    def test_laa_scenario_smod_3(self):
        # Client - 1 Property Joint Owned
        # MV £300,000, Mortgage £34,560, SMOD, Equity Disregard
        # Capital £0.00 Pass

        calc = CapitalCalculator(properties=[self.make_property(30000000, 3456000, 50, True, True)])
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0], "property_capital": 0, "liquid_capital": 0})

    def test_laa_scenario_smod_4(self):
        # Client - 2 Properties Both SMOD
        # MV £136,000, Mortgage £75,000, SMOD, Equity Disregard
        # MV £120,000, Mortgage £25,000, SMOD
        # Capital £56,000 (all from 2nd Property) Fail

        calc = CapitalCalculator(
            properties=[
                self.make_property(13600000, 7500000, 100, True, True),
                self.make_property(12000000, 2500000, 100, True, False),
            ]
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 5600000)
        self.assertEqual(calc.main_property["equity"], 0)
        self.assertEqual(calc.other_properties[0]["equity"], 5600000)
        self.assertDictEqual(
            calc.calcs, {"property_equities": [0, 5600000], "property_capital": 5600000, "liquid_capital": 0}
        )

    def test_laa_scenario_smod_5(self):
        # Client - 2 Properties, Second SMOD
        # MV £136,000, Mortgage £75,000, Equity Disregard
        # MV £120,000, Mortgage £25,000, SMOD Y
        # Capital £0.00 Pass

        calc = CapitalCalculator(
            properties=[
                self.make_property(13600000, 7500000, 100, False, True),
                self.make_property(12000000, 2500000, 100, True, False),
            ]
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0})

    def test_laa_scenario_smod_6(self):
        # Client - 1 Property, Doesn't reside, SMOD
        # MV £145,000, Mortgage £45,670, SMOD
        # Capital £0.00 Pass

        calc = CapitalCalculator(properties=[self.make_property(14500000, 45667000, 100, True, False)])
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0], "property_capital": 0, "liquid_capital": 0})

    def test_laa_scenario_smod_7(self):
        # Client and Partner 1 Property each, Not SMOD
        # MV £156,000, Mortgage £89,000, Equity Disregard
        # MV £129,000, Mortgage £45,000
        # Capital £1,000 from First, £84,000 from Second Fail

        # from @marco, it doesn't matter which property is the
        # main one as no SMOD applies

        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, False, True),
                self.make_property(12900000, 4500000, 100, False, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 8500000,
                "main_property_equity": 100000,
                "other_property_equity": 8400000,
                "calcs": {"property_equities": [100000, 8400000], "property_capital": 8500000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 8400000,
                "main_property_equity": 0,
                "other_property_equity": 8400000,
                "calcs": {"property_equities": [0, 8400000], "property_capital": 8400000, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_smod_8(self):
        # Client and Partner 1 Property each, First SMOD
        # MV £156,000, Mortgage £89,000, SMOD, Equity Disregard
        # MV £129,000, Mortgage £45,000
        # Capital £84,000 from Second, Fail

        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, True, True),
                self.make_property(12900000, 4500000, 100, False, False),
            ]
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 8400000)
        self.assertEqual(calc.main_property["equity"], 0)
        self.assertEqual(calc.other_properties[0]["equity"], 8400000)
        self.assertDictEqual(
            calc.calcs, {"property_equities": [0, 8400000], "property_capital": 8400000, "liquid_capital": 0}
        )

    def test_laa_scenario_smod_9(self):
        # Client and Partner 1 Property each, Second SMOD
        # MV £156,000, Mortgage £89,000, Equity Disregard
        # MV £129,000, Mortgage £45,000, SMOD
        # Capital £1,000 from First, Pass

        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, False, True),
                self.make_property(12900000, 4500000, 100, True, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 100000,
                "main_property_equity": 100000,
                "other_property_equity": 0,
                "calcs": {"property_equities": [100000, 0], "property_capital": 100000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 0,
                "main_property_equity": 0,
                "other_property_equity": 0,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_smod_10(self):
        # Client and Partner 1 Property each, Both SMOD
        # MV £156,000, Mortgage £89,000, SMOD, Equity Disregard
        # MV £129,000, Mortgage £45,000, SMOD
        # Capital £84,000 from Second, Fail

        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, True, True),
                self.make_property(12900000, 4500000, 100, True, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 8400000,
                "main_property_equity": 0,
                "other_property_equity": 8400000,
                "calcs": {"property_equities": [0, 8400000], "property_capital": 8400000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 5100000,
                "main_property_equity": 0,
                "other_property_equity": 5100000,
                "calcs": {"property_equities": [0, 5100000], "property_capital": 5100000, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_smod_11(self):
        # Client and Partner 1 Property each, Reside in Partner's Property, First SMOD
        # MV £156,000, Mortgage £89,000
        # MV £129,000, Mortgage £45,000, SMOD, Equity Disregard
        # Capital £67,000 Fail

        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, False, False),
                self.make_property(12900000, 4500000, 100, True, True),
            ]
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 6700000)
        self.assertDictEqual(
            calc.calcs, {"property_equities": [6700000, 0], "property_capital": 6700000, "liquid_capital": 0}
        )

    def test_laa_scenario_smod_12(self):
        # Client and Partner 1 Property each, Reside in Partner's Property, Second SMOD
        # MV £156,000, Mortgage £89,000, SMOD
        # MV £129,000, Mortgage £45,000,Equity Disregard
        # Capital £18,000 Fail

        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, True, False),
                self.make_property(12900000, 4500000, 100, False, True),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 1800000,
                "calcs": {"property_equities": [0, 1800000], "property_capital": 1800000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 0,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_smod_13(self):
        # Client and Partner 1 Property each, Reside in Partner's Property, Both SMOD
        # MV £156,000, Mortgage £89,000, SMOD
        # MV £129,000, Mortgage £45,000, SMOD, Equity Disregard
        # Capital £67,000 Fail

        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, True, False),
                self.make_property(12900000, 4500000, 100, True, True),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 6700000,
                "calcs": {"property_equities": [6700000, 0], "property_capital": 6700000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 5100000,
                "calcs": {"property_equities": [5100000, 0], "property_capital": 5100000, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_smod_14(self):
        # Client - 2 Properties, Both SMOD, Joint Owned
        # MV £136,000, Mortgage £120,000, 50%, SMOD, Equity Disregard
        # MV £86,000, Mortgage £45,000, 50%, SMOD
        # Capital £0.00 Pass

        calc = CapitalCalculator(
            properties=[
                self.make_property(13600000, 12000000, 50, True, True),
                self.make_property(8600000, 4500000, 50, True, False),
            ]
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0})

    def test_laa_scenario_smod_15(self):
        # Client - 2 Properties, Both SMOD, High Value, Joint Owned
        # MV £340,000, Mortgage £220,500, 50%, SMOD, Equity Disregard
        # MV £210,000, Mortgage £195,000, 50%, SMOD
        # Capital £55,000 Fail

        calc = CapitalCalculator(
            properties=[
                self.make_property(34000000, 22000000, 50, True, True),
                self.make_property(21000000, 19500000, 50, True, False),
            ]
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 5500000,
                "calcs": {"property_equities": [0, 5500000], "property_capital": 5500000, "liquid_capital": 0},
            },
            "post_mortgage_cap_removal": {
                "capital": 0,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 0},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_scenario_assets_smod_1(self):
        # The applicant has a home worth £120,000 and the mortgage is £80,000.
        # SMOD on main property
        # The client also has full access to a joint savings account,
        # account balance £9,000 disputed

        calc = CapitalCalculator(
            properties=[self.make_property(12000000, 8000000, 100, True, True)], disputed_liquid_capital=10000000
        )
        capital = calc.calculate_capital()

        self.assertEqual(capital, 4000000)
        self.assertEqual(calc.main_property["equity"], 0)
        self.assertDictEqual(calc.calcs, {"property_equities": [0], "property_capital": 0, "liquid_capital": 4000000})

    def test_laa_scenario_assets_smod_A50(self):
        # Client, No Partner, No Children, Passported (IS), No Property
        # Undisputed Assets Savings £5000 Investments £0 IOV £500 Owed £0
        # Disputed Assets Savings £0 Investments £2,500, IOV £500 Owed £0
        # Pass
        calc = CapitalCalculator(properties=[], non_disputed_liquid_capital=550000, disputed_liquid_capital=300000)
        capital = calc.calculate_capital()
        self.assertEqual(capital, 550000)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 550000})

    def test_laa_scenario_assets_smod_A51(self):
        # Client, No Partner, No Children, Passported (IS), No Property
        # Undisputed Assets Savings £5000 Investments £2500 IOV £499.99 Owed £0
        # Disputed Assets Savings £0 Investments £2,500, IOV £500 Owed £0
        # Just Pass
        calc = CapitalCalculator(properties=[], non_disputed_liquid_capital=799999, disputed_liquid_capital=300000)
        capital = calc.calculate_capital()
        self.assertEqual(capital, 799999)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 799999})

    def test_laa_scenario_assets_smod_A52(self):
        # Client, No Partner, No Children, Passported (IS), No Property
        # Undisputed Assets Savings £5000 Investments £2500 IOV £501 Owed £0
        # Disputed Assets Savings £0 Investments £2,500, IOV £500 Owed £0
        # Fail
        calc = CapitalCalculator(properties=[], non_disputed_liquid_capital=800100, disputed_liquid_capital=300000)
        capital = calc.calculate_capital()
        self.assertEqual(capital, 800100)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 800100})

    def test_laa_scenario_assets_smod_A53(self):
        # Client, Partner, No Children, Passported (IS), No Property
        # Undisputed Assets Savings £1000 Investments £1500 IOV £0 Owed £0
        # Partner Assets Savings £567.89 Investments £1,200 IOV £600 Owed £0
        # Disputed Assets Savings £0 Investments £10,000, IOV £12,000 Owed £0
        # Pass
        calc = CapitalCalculator(properties=[], non_disputed_liquid_capital=250000, disputed_liquid_capital=236789)
        capital = calc.calculate_capital()
        self.assertEqual(capital, 250000)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 250000})

    def test_laa_scenario_assets_smod_A54(self):
        # Client, Partner, No Children, Passported (IS), No Property
        # Undisputed Assets Savings £4,000, Investments £1,000, IOV £0, Owed £0
        # Partner Assets Savings £1,000, Investments £1,500, IOV £499.99 Owed £0
        # Disputed Assets Savings £0, Investments £1,000 IOV £12,000 Owed £0
        # Just Pass
        calc = CapitalCalculator(
            properties=[],
            non_disputed_liquid_capital=400000 + 100000 + 100000 + 150000 + 49999,
            disputed_liquid_capital=100000 + 1200000,
        )
        capital = calc.calculate_capital()
        self.assertEqual(capital, 799999)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 799999})

    def test_laa_scenario_assets_smod_A55(self):
        # Client, Partner, No Children, Passported (IS), No Property
        # Undisputed Assets Savings £4,000, Investments £1,000, IOV £0, Owed £0
        # Partner Assets Savings £1,000.01, Investments £1,500, IOV £500 Owed £0
        # Disputed Assets Savings £0, Investments £1,000 IOV £12,000 Owed £0
        # Fail
        calc = CapitalCalculator(
            properties=[],
            non_disputed_liquid_capital=400000 + 100000 + 100001 + 150000 + 50000,
            disputed_liquid_capital=100000 + 1200000,
        )
        capital = calc.calculate_capital()
        self.assertEqual(capital, 800001)
        self.assertDictEqual(calc.calcs, {"property_equities": [], "property_capital": 0, "liquid_capital": 800001})

    def test_laa_scenario_assets_smod_A56(self):
        # Client, Partner, No Children, Passported (IS), Property
        # MV £156,000, Mortgage £89,000, Equity Disregard
        # MV £129,000, Mortgage £45,000, SMOD
        # Capital from property £1,000, SMOD remaining after property £16,000
        # Undisputed Assets Savings £1000 Investments £1500 IOV £0 Owed £0
        # Partner Assets Savings £567.89 Investments £1,200 IOV £600 Owed £0
        # Disputed Assets Savings £0 Investments £10,000, IOV £12,000 Owed £0
        # Fail
        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, False, True),
                self.make_property(12900000, 4500000, 100, True, False),
            ],
            non_disputed_liquid_capital=100000 + 150000 + 56789 + 120000 + 60000,
            disputed_liquid_capital=1000000 + 1200000,
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 1186789,
                "main_property_equity": 100000,
                "calcs": {"property_equities": [100000, 0], "property_capital": 100000, "liquid_capital": 1086789},
            },
            "post_mortgage_cap_removal": {
                "capital": 1086789,
                "main_property_equity": 0,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 1086789},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)

    def test_laa_scenario_assets_smod_A57(self):
        # Client, Partner, No Children, Passported (IS), Property
        # MV £156,000, Mortgage £89,000, Equity Disregard
        # MV £129,000, Mortgage £45,000, SMOD
        # Capital from property £1,000, SMOD remaining after property £16,000
        # Undisputed Assets Savings £3000 Investments £1500 IOV £499.99 Owed £0
        # Partner Assets Savings £1,000, Investments £1,000
        # Disputed Assets Savings £0 Investments £2,500, IOV £500 Owed £0
        # Just Pass (£7,999.99 capital and £13,000 SMOD remaining)
        calc = CapitalCalculator(
            properties=[
                self.make_property(15600000, 8900000, 100, False, True),
                self.make_property(12900000, 4500000, 100, True, False),
            ],
            non_disputed_liquid_capital=300000 + 150000 + 49999 + 100000 + 100000,
            disputed_liquid_capital=250000 + 50000,
        )
        capital = calc.calculate_capital()

        expected_results = {
            "pre_mortgage_cap_removal": {
                "capital": 799999,
                "main_property_equity": 100000,
                "calcs": {"property_equities": [100000, 0], "property_capital": 100000, "liquid_capital": 699999},
            },
            "post_mortgage_cap_removal": {
                "capital": 699999,
                "main_property_equity": 0,
                "calcs": {"property_equities": [0, 0], "property_capital": 0, "liquid_capital": 699999},
            },
        }
        self._assert_calculations(expected_results[self.expected_results_key], calc, capital)


class CalculatorTestBase(MortgageCapRemovalMixin, unittest.TestCase):
    def get_default_case_data(self, **kwargs):
        """
        gives default case_data with each kwarg
        overridden

        :param kwargs: things to overwrite in the default case_data
        :return: CaseData object with default values
        """
        return CaseData(**fixtures.get_default_case_data(**kwargs))


class TestCalculator(CalculatorTestBase):
    def setUp(self):
        self.default_calculator = EligibilityChecker(self.get_default_case_data())

    def test_gross_income_is_eligible(self):
        too_little_money = constants.BASE_LIMIT - 1
        case_data = self.get_default_case_data(you__income__earnings=too_little_money)
        checker = EligibilityChecker(case_data)
        self.assertTrue(checker.is_gross_income_eligible())
        self.assertDictEqual(checker.calcs, {"gross_income": constants.BASE_LIMIT - 1})

    def test_gross_income_is_ineligible(self):
        too_much_money = constants.BASE_LIMIT + 1
        case_data = self.get_default_case_data(you__income__earnings=too_much_money)
        checker = EligibilityChecker(case_data)
        self.assertFalse(checker.is_gross_income_eligible())
        self.assertDictEqual(checker.calcs, {"gross_income": constants.BASE_LIMIT + 1})

    def test_base_limit_gross_income_is_ineligible(self):
        """
        TEST: gross_income limit doesn't rise for 1-4 children.
        Should reject someone for having income more than 2657
        """
        too_much_money = constants.BASE_LIMIT + 1
        for dep_children in range(1, constants.INCLUSIVE_CHILDREN_BASE + 1):
            case_data = self.get_default_case_data(
                you__income__earnings=too_much_money, facts__dependants_young=dep_children, facts__dependants_old=0
            )
            checker = EligibilityChecker(case_data)
            self.assertFalse(checker.is_gross_income_eligible())
            self.assertDictEqual(checker.calcs, {"gross_income": too_much_money})

    def test_base_limit_gross_income_is_eligible(self):
        """
        if you have > 4 children then earning 1 more than base limit
        should be fine.
        """
        too_much_money = constants.BASE_LIMIT + 1
        case_data = self.get_default_case_data(
            you__income__earnings=too_much_money, facts__dependants_young=5, facts__dependants_old=0
        )
        checker = EligibilityChecker(case_data)
        self.assertTrue(checker.is_gross_income_eligible())
        self.assertDictEqual(checker.calcs, {"gross_income": too_much_money})


class TestApplicantOnBenefitsCalculator(CalculatorTestBase):
    """
    An applicant on passported benefits should be eligible
    solely on their disposable capital income test.

    They should not be asked income questions.
    """

    def test_applicant_on_single_benefits_no_capital_is_eligible(self):
        case_data = self.get_default_case_data(facts__on_passported_benefits=True)
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        self.assertEqual(case_data.you.income.total, 0)
        self.assertEqual(case_data.total_income, 0)
        self.assertTrue(is_elig)
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 0,
                "disposable_capital_assets": 0,
                "property_equities": [],
                "property_capital": 0,
                "liquid_capital": 0,
            },
        )

    def test_applicant_on_single_benefits_no_capital_has_property_is_eligible(self):
        case_data = self.get_default_case_data(
            facts__on_passported_benefits=True,
            property_data=[{"value": 10800000, "mortgage_left": 0, "share": 100, "disputed": False, "main": True}],
        )
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        self.assertEqual(case_data.you.income.total, 0)
        self.assertEqual(case_data.total_income, 0)
        self.assertTrue(is_elig)
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 0,
                "disposable_capital_assets": 800000,
                "property_equities": [800000],
                "property_capital": 800000,
                "liquid_capital": 0,
            },
        )


class TestApplicantPensionerCoupleOnBenefits(CalculatorTestBase):
    def _test_pensioner_on_benefits(self, property_value, mortgage, other_assets):
        case_data = self.get_default_case_data(
            facts__on_passported_benefits=True,
            facts__is_you_or_your_partner_over_60=True,
            property_data=[
                {"value": property_value, "mortgage_left": mortgage, "share": 100, "disputed": False, "main": True}
            ],
        )
        case_data.you.savings.asset_balance = other_assets

        return EligibilityChecker(case_data)

    def test_pensioner_250k_house_100k_mort_0_savings(self):
        """
        if over 60 and on benefits 250k house with 100k mortgage should pass
        """
        checker = self._test_pensioner_on_benefits(25000000, 10000000, 0)
        self.assertTrue(checker.is_eligible())
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 10000000,
                "gross_income": 0,
                "partner_allowance": 0,
                "disposable_income": 0,
                "dependants_allowance": 0,
                "employment_allowance": 0,
                "partner_employment_allowance": 0,
                "property_capital": 5000000,
                "property_equities": [5000000],
                "liquid_capital": 0,
                "disposable_capital_assets": 0,
            },
        )

    def test_pensioner_300k1p_house_100k1p_mort_799999_savings(self):
        """
        if over 60 and on benefits, 300K.01 house with 100K.01 mortgage and
        7999.99 of other assets should pass.
        """
        checker = self._test_pensioner_on_benefits(30000001, 10000001, 79999)
        expected_results = {
            "pensioner_disregard": 10000000,
            "gross_income": 0,
            "partner_allowance": 0,
            "disposable_income": 0,
            "dependants_allowance": 0,
            "employment_allowance": 0,
            "partner_employment_allowance": 0,
            "liquid_capital": 79999,
        }
        expected_property_results = {
            "pre_mortgage_cap_removal": {
                "property_capital": 10000001,
                "property_equities": [10000001],
                "disposable_capital_assets": 80000,
            },
            "post_mortgage_cap_removal": {
                "property_capital": 10000000,
                "property_equities": [10000000],
                "disposable_capital_assets": 79999,
            },
        }
        expected_results.update(expected_property_results[self.expected_results_key])
        self.assertTrue(checker.is_eligible())
        self.assertDictEqual(checker.calcs, expected_results)

    def test_pensioner_300k2p_house_100k1p_mort_799999_savings(self):
        """
        if over 60 and on benefits, 300K.02 house with 100K.01 mortgage and
        7999.99 of other assets should fail.
        """
        checker = self._test_pensioner_on_benefits(30000002, 10000001, 79999)

        expected_results = {
            "pensioner_disregard": 10000000,
            "gross_income": 0,
            "partner_allowance": 0,
            "disposable_income": 0,
            "dependants_allowance": 0,
            "employment_allowance": 0,
            "partner_employment_allowance": 0,
            "liquid_capital": 79999,
        }
        expected_property_results = {
            "pre_mortgage_cap_removal": {
                "property_capital": 10000002,
                "property_equities": [10000002],
                "disposable_capital_assets": 80001,
            },
            "post_mortgage_cap_removal": {
                "property_capital": 10000001,
                "property_equities": [10000001],
                "disposable_capital_assets": 80000,
            },
        }
        expected_results.update(expected_property_results[self.expected_results_key])

        self.assertTrue(checker.is_eligible())
        self.assertDictEqual(checker.calcs, expected_results)


class TestApplicantSinglePensionerNotOnBenefits(CalculatorTestBase):
    def _test_pensioner(self, case_data):
        checker = EligibilityChecker(case_data)
        is_elig = checker.is_eligible()
        return is_elig, checker

    def test_pensioner_200k2p_house_100k1p_mort_800001_savings(self):
        """
        if over 60 and on benefits, 300K.02 house with 100K.01 mortgage and
        8000.01+.01+.01 of other assets should fail.
        """

        case_data = self.get_default_case_data(
            facts__on_passported_benefits=False,
            facts__is_you_or_your_partner_over_60=True,
            property_data=[
                {"value": 20000002, "mortgage_left": 10000001, "share": 100, "disputed": False, "main": True}
            ],
            you__income__earnings=31506,
            you__income__other_income=59001,
            you__savings__bank_balance=800001,
            you__savings__investment_balance=1,
            you__savings__asset_balance=1,
            you__savings__credit_balance=1,
            you__deductions__mortgage=54501,
            you__deductions__rent=2,
            you__deductions__income_tax=2,
            you__deductions__national_insurance=1,
            you__deductions__maintenance=1,
            you__deductions__childcare=1,
            you__deductions__criminal_legalaid_contributions=1,
        )
        is_elig, checker = self._test_pensioner(case_data)

        expected_results = {
            "pensioner_disregard": 0,
            "gross_income": 90507,
            "partner_allowance": 0,
            "disposable_income": 31501,
            "dependants_allowance": 0,
            "employment_allowance": 4500,
            "partner_employment_allowance": 0,
            "liquid_capital": 800004,
        }
        expected_property_results = {
            "pre_mortgage_cap_removal": {
                "property_capital": 2,
                "property_equities": [2],
                "disposable_capital_assets": 800006,
            },
            "post_mortgage_cap_removal": {
                "property_capital": 1,
                "property_equities": [1],
                "disposable_capital_assets": 800005,
            },
        }
        expected_results.update(expected_property_results[self.expected_results_key])

        self.assertFalse(is_elig)
        self.assertDictEqual(checker.calcs, expected_results)

    def test_pensioner_limit_10k_diregard_fail(self):
        """
        pensioner over 60, no property 18,000.01 savings
        310 other income:
        should be ineligible.
        """
        case_data = self.get_default_case_data(
            facts__on_passported_benefits=False,
            facts__is_you_or_your_partner_over_60=True,
            you__income__other_income=31000,
            you__savings__bank_balance=1800001,
        )

        is_elig, checker = self._test_pensioner(case_data)

        self.assertFalse(is_elig)
        self.assertDictEqual(
            checker.calcs,
            {
                "pensioner_disregard": 1000000,
                "gross_income": 31000,
                "partner_allowance": 0,
                "disposable_income": 31000,
                "dependants_allowance": 0,
                "employment_allowance": 0,
                "partner_employment_allowance": 0,
                "property_capital": 0,
                "property_equities": [],
                "liquid_capital": 1800001,
                "disposable_capital_assets": 800001,
            },
        )


class GrossIncomeTestCase(CalculatorTestBase):
    def test_gross_income(self):
        """
        TEST: Gross income == mocked total income
        """
        case_data = mock.MagicMock(total_income=500)
        ec = EligibilityChecker(case_data)
        self.assertEqual(ec.gross_income, 500)

    def test_on_passported_benefits_is_gross_income_eligible(self):
        """
        TEST: Gross income not called
        """
        case_data = mock.MagicMock()
        type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=True)
        type(case_data).total_income = mock.PropertyMock()
        with mock.patch.object(
            EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
        ) as mocked_gross_income:
            ec = EligibilityChecker(case_data)
            self.assertTrue(ec.is_gross_income_eligible())
            self.assertFalse(case_data.total_income.called)
            self.assertFalse(mocked_gross_income.called)

    def test_is_gross_income_eligible_on_limit(self):
        """
        TEST: eligibility depends on mocked limit
        """
        with mock.patch.object(constants, "get_gross_income_limit") as mocked_get_gross_income_limit:
            mocked_get_gross_income_limit.return_value = 500
            case_data = mock.MagicMock()
            type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=False)
            type(case_data.facts).dependant_children = mock.PropertyMock(return_value=0)
            with mock.patch.object(
                EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
            ) as mocked_gross_income:
                mocked_gross_income.return_value = 500
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_gross_income_eligible())
                mocked_get_gross_income_limit.assert_called_with(0)
                mocked_gross_income.assert_called_once_with()

    def test_is_gross_income_eligible_under_limit(self):
        """
        TEST: eligibility depends on mocked limit
        """
        with mock.patch.object(constants, "get_gross_income_limit") as mocked_get_gross_income_limit:
            mocked_get_gross_income_limit.return_value = 500
            case_data = mock.MagicMock()
            type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=False)
            type(case_data.facts).dependant_children = mock.PropertyMock(return_value=0)
            with mock.patch.object(
                EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
            ) as mocked_gross_income:
                mocked_gross_income.return_value = 499
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_gross_income_eligible())
                mocked_get_gross_income_limit.assert_called_with(0)
                mocked_gross_income.assert_called_once_with()

    def test_is_gross_income_not_eligible(self):
        """
        TEST: eligibility depends on mocked limit
        """
        with mock.patch.object(constants, "get_gross_income_limit") as mocked_get_gross_income_limit:
            mocked_get_gross_income_limit.return_value = 500
            case_data = mock.MagicMock()
            type(case_data.facts).on_passported_benefits = mock.PropertyMock(return_value=False)
            type(case_data.facts).dependant_children = mock.PropertyMock(return_value=0)
            with mock.patch.object(
                EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
            ) as mocked_gross_income:
                mocked_gross_income.return_value = 501
                ec = EligibilityChecker(case_data)
                self.assertFalse(ec.is_gross_income_eligible())
                mocked_get_gross_income_limit.assert_called_with(0)
                mocked_gross_income.assert_called_once_with()


class DisposableIncomeTestCase(unittest.TestCase):
    def test_disposable_income_with_children(self):
        """
        TEST: with mocked gross_income,
        has_partner = True

        we check that
        disposable capital returns gross_income minus
        allowance for dependent children > 1,
        income_tax_and_ni > 1,
        maintainable > 1
        has_employment_earnings True
        self employed = False
        mortgage_or_rent > 1
        childcare > 1
        criminal_legalaid_contributions > 1

        should_aggregate_partner = True,
            partner.income_tax_and_ni > 1
            partner.maintenance > 1
            partner.has_employment_earnings True
            partner.self_employed = False
            partner.childcare > 1
            partner.criminal_legalaid_contributions > 1

        should be equal to sum of above random values

        """
        facts = Facts(
            has_partner=True, dependants_young=random.randint(2, 5), dependants_old=0, is_partner_opponent=False
        )
        you = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax=random.randint(50, 1000),
                national_insurance=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage=random.randint(50, 1000),
                rent=random.randint(50, 1000),
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000),
            ),
            income=mock.MagicMock(self_employed=False, has_employment_earnings=True),
        )
        partner = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax=random.randint(50, 1000),
                national_insurance=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage=random.randint(50, 1000),
                rent=random.randint(50, 1000),
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000),
            ),
            income=mock.MagicMock(self_employed=False, has_employment_earnings=True),
        )

        case_data = mock.MagicMock(facts=facts, you=you, partner=partner)

        with mock.patch.object(
            EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
        ) as mocked_gross_income:
            mocked_gross_income.return_value = random.randint(5000, 100000)

            ec = EligibilityChecker(case_data)

            expected_value = (
                ec.gross_income
                - constants.PARTNER_ALLOWANCE
                - (facts.dependants_young + facts.dependants_old) * constants.CHILD_ALLOWANCE
                - you.deductions.income_tax
                - you.deductions.national_insurance
                - you.deductions.maintenance
                - you.deductions.mortgage
                - you.deductions.rent
                - you.deductions.childcare
                - you.deductions.criminal_legalaid_contributions
                - partner.deductions.income_tax
                - partner.deductions.national_insurance
                - partner.deductions.maintenance
                - partner.deductions.mortgage
                - partner.deductions.rent
                - partner.deductions.childcare
                - partner.deductions.criminal_legalaid_contributions
                - constants.EMPLOYMENT_COSTS_ALLOWANCE
                - constants.EMPLOYMENT_COSTS_ALLOWANCE
            )

            self.assertEqual(expected_value, ec.disposable_income)

    def test_disposable_income_single_without_children_below_cap(self):
        """
        TEST: with mocked gross_income,
        has_partner = False
        dependent_children = 0

        we check that
        disposable capital returns gross_income minus
        allowance for dependent children: 0,
        income_tax_and_ni > 1,
        maintainable > 1
        has_employment_earnings True
        self employed = True
        mortgage_or_rent > 1  (and below childless housing cap)
        childcare > 1
        criminal_legalaid_contributions > 1

        should be equal to sum of above random values

        """
        facts = Facts(has_partner=False, dependants_young=0, dependants_old=0, is_partner_opponent=False)
        you = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax=random.randint(50, 1000),
                national_insurance=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage=constants.CHILDLESS_HOUSING_CAP - 1000,
                rent=0,
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000),
            ),
            income=mock.MagicMock(self_employed=True, has_employment_earnings=True),
        )

        case_data = mock.MagicMock(facts=facts, you=you)

        with mock.patch.object(
            EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
        ) as mocked_gross_income:
            mocked_gross_income.return_value = random.randint(5000, 100000)

            ec = EligibilityChecker(case_data)

            expected_value = (
                ec.gross_income
                - you.deductions.income_tax
                - you.deductions.national_insurance
                - you.deductions.maintenance
                - you.deductions.mortgage
                - you.deductions.rent
                - you.deductions.childcare
                - you.deductions.criminal_legalaid_contributions
            )

            self.assertEqual(expected_value, ec.disposable_income)

    def test_disposable_income_single_without_children_above_cap(self):
        """
        TEST: with mocked gross_income,
        has_partner = False
        dependent_children = 0

        we check that
        disposable capital returns gross_income minus
        allowance for dependent children: 0,
        income_tax_and_ni > 1,
        maintainable > 1
        has_employment_earnings = True
        self employed = True
        mortgage_or_rent > 1  (and above childless housing cap)
        childcare > 1
        criminal_legalaid_contributions > 1

        should be equal to sum of above random values

        Mortgage or rent is capped to
            constants.disposable_income.CHILDLESS_HOUSING_CAP
        """
        facts = Facts(has_partner=False, dependants_young=0, dependants_old=0, is_partner_opponent=False)
        you = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax=random.randint(50, 1000),
                national_insurance=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage=constants.CHILDLESS_HOUSING_CAP + 1000,
                rent=0,
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000),
            ),
            income=mock.MagicMock(self_employed=True, has_employment_earnings=True),
        )

        case_data = mock.MagicMock(facts=facts, you=you)

        with mock.patch.object(
            EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
        ) as mocked_gross_income:
            mocked_gross_income.return_value = random.randint(5000, 100000)
            ec = EligibilityChecker(case_data)

            expected_value = (
                ec.gross_income
                - you.deductions.income_tax
                - you.deductions.national_insurance
                - you.deductions.maintenance
                - constants.CHILDLESS_HOUSING_CAP
                - you.deductions.childcare
                - you.deductions.criminal_legalaid_contributions
            )

            self.assertEqual(expected_value, ec.disposable_income)

    def test_disposable_income_no_employment_allowance_if_no_earnings(self):
        """
        TEST: with mocked gross_income.
        The final value should NOT detract EMPLOYMENT ALLOWANCE*2 because
            has_employment_earnings = False for 'you' and 'partner'

        has_partner = True
        allowance for dependent children > 1,
        income_tax_and_ni > 1,
        maintainable > 1
        has_employment_earnings = False
        self employed = False
        mortgage_or_rent > 1
        childcare > 1
        criminal_legalaid_contributions > 1

        should_aggregate_partner = True,
            partner.income_tax_and_ni > 1
            partner.maintenance > 1
            partner.has_employment_earnings = False
            partner.self_employed = False
            partner.childcare > 1
            partner.criminal_legalaid_contributions > 1

        Disposable income should be equal to the sum of above random values

        """
        facts = Facts(
            has_partner=True, dependants_young=random.randint(2, 5), dependants_old=0, is_partner_opponent=False
        )
        you = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax=random.randint(50, 1000),
                national_insurance=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage=random.randint(50, 1000),
                rent=random.randint(50, 1000),
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000),
            ),
            income=mock.MagicMock(self_employed=False, has_employment_earnings=False),
        )
        partner = mock.MagicMock(
            deductions=mock.MagicMock(
                income_tax=random.randint(50, 1000),
                national_insurance=random.randint(50, 1000),
                maintenance=random.randint(50, 1000),
                mortgage=random.randint(50, 1000),
                rent=random.randint(50, 1000),
                childcare=random.randint(50, 1000),
                criminal_legalaid_contributions=random.randint(50, 1000),
            ),
            income=mock.MagicMock(self_employed=False, has_employment_earnings=False),
        )

        case_data = mock.MagicMock(facts=facts, you=you, partner=partner)

        with mock.patch.object(
            EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
        ) as mocked_gross_income:
            mocked_gross_income.return_value = random.randint(5000, 100000)

            ec = EligibilityChecker(case_data)

            facts_dependants = facts.dependants_young + facts.dependants_old
            expected_value = (
                ec.gross_income
                - constants.PARTNER_ALLOWANCE
                - facts_dependants * constants.CHILD_ALLOWANCE
                - you.deductions.income_tax
                - you.deductions.national_insurance
                - you.deductions.maintenance
                - you.deductions.mortgage
                - you.deductions.rent
                - you.deductions.childcare
                - you.deductions.criminal_legalaid_contributions
                - partner.deductions.income_tax
                - partner.deductions.national_insurance
                - partner.deductions.maintenance
                - partner.deductions.mortgage
                - partner.deductions.rent
                - partner.deductions.childcare
                - partner.deductions.criminal_legalaid_contributions
            )

            self.assertEqual(expected_value, ec.disposable_income)

    def test_on_passported_benefits_is_disposable_income_eligible(self):
        """
        TEST: disposable income not called
        """
        facts = mock.MagicMock(on_passported_benefits=True)
        case_data = mock.MagicMock(facts=facts)

        with mock.patch.object(
            EligibilityChecker, "gross_income", new_callable=mock.PropertyMock
        ) as mocked_gross_income:
            ec = EligibilityChecker(case_data)

            self.assertTrue(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_gross_income.called, False)

    def test_is_disposable_income_eligible_on_limit(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(on_passported_benefits=False)
        case_data = mock.MagicMock(facts=facts)

        with mock.patch.object(
            EligibilityChecker, "disposable_income", new_callable=mock.PropertyMock
        ) as mocked_disposable_income:
            mocked_disposable_income.return_value = constants.LIMIT
            ec = EligibilityChecker(case_data)

            self.assertTrue(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_disposable_income.called, True)

    def test_is_disposable_income_eligible_under_limit(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(on_passported_benefits=False)
        case_data = mock.MagicMock(facts=facts)

        with mock.patch.object(
            EligibilityChecker, "disposable_income", new_callable=mock.PropertyMock
        ) as mocked_disposable_income:
            mocked_disposable_income.return_value = constants.LIMIT - 1000
            ec = EligibilityChecker(case_data)

            self.assertTrue(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_disposable_income.called, True)

    def test_is_disposable_income_not_eligible(self):
        """
        TEST: mock disposable income
        """
        facts = mock.MagicMock(on_passported_benefits=False)
        case_data = mock.MagicMock(facts=facts)

        with mock.patch.object(
            EligibilityChecker, "disposable_income", new_callable=mock.PropertyMock
        ) as mocked_disposable_income:
            mocked_disposable_income.return_value = constants.LIMIT + 1
            ec = EligibilityChecker(case_data)

            self.assertFalse(ec.is_disposable_income_eligible())
            self.assertEqual(mocked_disposable_income.called, True)


class DisposableCapitalTestCase(unittest.TestCase):
    def test_disposable_capital_assets_subtracts_pensioner_disregard(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            is_you_or_partner_over_60 = True
            properties_value == mortgages left == 0

            non_disputed_liquid_capital > pensioner_disregard

        result:
            disposable_capital = non_disputed_liquid_capital - pensioner_disregard
        """
        facts = mock.MagicMock(has_disputed_partner=False, is_you_or_your_partner_over_60=True)

        case_data = mock.MagicMock(
            facts=facts,
            non_disputed_liquid_capital=random.randint(6000000, 8000000),
            disputed_liquid_capital=0,
            property_capital=(0, 0),
        )

        pensioner_disregard_limit = 5000000
        with mock.patch.object(constants, "PENSIONER_DISREGARD_LIMIT_LEVELS") as mocked_pensioner_disregard:
            mocked_pensioner_disregard.get.return_value = pensioner_disregard_limit
            ec = EligibilityChecker(case_data)

            expected_value = case_data.non_disputed_liquid_capital - pensioner_disregard_limit

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, True)

    def test_disposable_capital_assets_subtracts_pensioner_disregard_but_cant_be_negative(self):
        """
        TEST:
            mocked liquid capital and property capital
            not disputed partner
            is_you_or_partner_over_60 = True
            properties_value == mortgages left == 0

            non_disputed_liquid_capital < pensioner_disregard

        result:
            disposable_capital = 0 (no negative numbers returned)
        """
        facts = mock.MagicMock(has_disputed_partner=False, is_you_or_your_partner_over_60=True)

        case_data = mock.MagicMock(
            facts=facts,
            non_disputed_liquid_capital=random.randint(50, 4999999),
            disputed_liquid_capital=0,
            property_capital=(0, 0),
        )

        pensioner_disregard_limit = 5000000
        with mock.patch.object(constants, "PENSIONER_DISREGARD_LIMIT_LEVELS") as mocked_pensioner_disregard:
            mocked_pensioner_disregard.get.return_value = pensioner_disregard_limit
            ec = EligibilityChecker(case_data)

            expected_value = 0

            self.assertEqual(expected_value, ec.disposable_capital_assets)
            self.assertEqual(mocked_pensioner_disregard.get.called, True)

    # here

    def test_is_disposable_capital_eligible_under_limit(self):
        """
        TEST: with mocked disposable_capital_assets and get_disposable_capital_limit
        """
        with mock.patch.object(constants, "get_disposable_capital_limit") as mocked_get_limit:
            mocked_get_limit.return_value = 700000
            case_data = mock.MagicMock()
            type(case_data).category = mock.PropertyMock(return_value=u"blah blah")
            with mock.patch.object(
                EligibilityChecker, "disposable_capital_assets", new_callable=mock.PropertyMock
            ) as mocked_disposable_capital_assets:
                mocked_disposable_capital_assets.return_value = 500
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_disposable_capital_eligible())
                mocked_get_limit.assert_called_once_with(u"blah blah")
                mocked_disposable_capital_assets.assert_called_once_with()

    def test_is_disposable_capital_eligible_on_limit(self):
        """
        TEST: with mocked disposable_capital_assets and get_disposable_capital_limit
        """
        with mock.patch.object(constants, "get_disposable_capital_limit") as mocked_get_limit:
            mocked_get_limit.return_value = 700000
            case_data = mock.MagicMock()
            type(case_data).category = mock.PropertyMock(return_value=u"blah blah")
            with mock.patch.object(
                EligibilityChecker, "disposable_capital_assets", new_callable=mock.PropertyMock
            ) as mocked_disposable_capital_assets:
                mocked_disposable_capital_assets.return_value = 700000
                ec = EligibilityChecker(case_data)
                self.assertTrue(ec.is_disposable_capital_eligible())
                mocked_get_limit.assert_called_once_with(u"blah blah")
                mocked_disposable_capital_assets.assert_called_once_with()

    def test_is_disposable_capital_not_eligible(self):
        """
        TEST: with mocked disposable_capital_assets and get_disposable_capital_limit
        """
        with mock.patch.object(constants, "get_disposable_capital_limit") as mocked_get_limit:
            mocked_get_limit.return_value = 700000
            case_data = mock.MagicMock()
            type(case_data).category = mock.PropertyMock(return_value=u"blah blah")
            with mock.patch.object(
                EligibilityChecker, "disposable_capital_assets", new_callable=mock.PropertyMock
            ) as mocked_disposable_capital_assets:
                mocked_disposable_capital_assets.return_value = 700001
                ec = EligibilityChecker(case_data)
                self.assertFalse(ec.is_disposable_capital_eligible())
                mocked_get_limit.assert_called_once_with(u"blah blah")
                mocked_disposable_capital_assets.assert_called_once_with()


class IsEligibleTestCase(unittest.TestCase):
    def create_a_dummy_citizen(
        self,
        is_category=False,
        is_passported=None,
        is_nass_benefits=None,
        is_gross_income=None,
        is_disposable_income=None,
        is_disposable_capital=None,
        has_passported_proceedings_letter=None,
    ):
        # gross_income, disposable_income, disposable_capital
        """
        This method creates a dummy citizen to use in the eligibility tests for legal aid.
        Set the category to either immigration, any other category or let it default to False.
        Set their passported benefits to either True, False or default to None.
        Set their NASS benefits to either True, False or default to None.
        Set their gross income to True (they are eligible), False (they are not eligible), or default to None.
        Set their disposable income to True (they are eligible), False (they are not eligible), or default to None.
        Set their disposable capital to True (they are eligible), False (they are not eligible), or default to None.
        """
        case_data = mock.MagicMock()
        case_data.category = is_category
        case_data.facts = mock.MagicMock()
        case_data.facts.has_passported_proceedings_letter = has_passported_proceedings_letter
        mocked_on_passported_benefits = mock.PropertyMock(return_value=is_passported)
        mocked_on_nass_benefits = mock.PropertyMock(return_value=is_nass_benefits)
        type(case_data.facts).on_passported_benefits = mocked_on_passported_benefits
        type(case_data.facts).on_nass_benefits = mocked_on_nass_benefits
        ec = EligibilityChecker(case_data)
        ec.is_gross_income_eligible = mock.MagicMock(return_value=is_gross_income)
        ec.is_disposable_income_eligible = mock.MagicMock(return_value=is_disposable_income)
        ec.is_disposable_capital_eligible = mock.MagicMock(return_value=is_disposable_capital)
        return ec, mocked_on_passported_benefits, mocked_on_nass_benefits

    def test_is_disposable_capital_not_eligible(self):
        """
        TEST: with mocked is_disposable_capital_eligible = False
        is_gross_income_eligible, is_disposable_income are not called
        asserts is_eligible = False
        """
        ec, mocked_on_passported_benefits, mocked_on_nass_benefits = self.create_a_dummy_citizen(
            is_passported=False, is_nass_benefits=False, is_disposable_capital=False
        )

        self.assertFalse(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        self.assertFalse(ec.is_gross_income_eligible.called)
        self.assertFalse(ec.is_disposable_income_eligible.called)

    def test_is_gross_income_not_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = False,
            is_disposable_capital = True

        is_disposable_income is not called
        asserts is_eligible = False
        """

        ec, mocked_on_passported_benefits, mocked_on_nass_benefits = self.create_a_dummy_citizen(
            is_passported=False, is_nass_benefits=False, is_gross_income=False, is_disposable_capital=True
        )

        self.assertFalse(mocked_on_passported_benefits.called)
        self.assertFalse(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        ec.is_gross_income_eligible.assert_called_once_with()
        self.assertFalse(ec.is_disposable_income_eligible.called)

    def test_is_disposable_income_not_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = True,
            is_disposable_capital = True,
            is_disposable_income = False
        asserts is_eligible = False
        """
        ec, mocked_on_passported_benefits, mocked_on_nass_benefits = self.create_a_dummy_citizen(
            is_passported=False,
            is_nass_benefits=False,
            is_disposable_income=False,
            is_gross_income=True,
            is_disposable_capital=True,
        )

        self.assertFalse(mocked_on_passported_benefits.called)
        self.assertFalse(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        ec.is_gross_income_eligible.assert_called_once_with()
        ec.is_disposable_capital_eligible.assert_called_once_with()

    def test_is_disposable_income_eligible(self):
        """
        TEST: with mocked:
            is_gross_income_eligible = True,
            is_disposable_capital = True,
            is_disposable_income = True
        asserts is_eligible = True
        """
        ec, mocked_on_passported_benefits, mocked_on_nass_benefits = self.create_a_dummy_citizen(
            is_passported=False,
            is_nass_benefits=False,
            is_disposable_income=True,
            is_gross_income=True,
            is_disposable_capital=True,
        )

        self.assertFalse(mocked_on_passported_benefits.called)
        self.assertTrue(ec.is_eligible())
        ec.is_disposable_capital_eligible.assert_called_once_with()
        ec.is_gross_income_eligible.assert_called_once_with()
        ec.is_disposable_capital_eligible.assert_called_once_with()

    def test_nass_benefit_is_eligible_only_if_is_category_is_immigration(self):
        """
        TEST: if citizen is on NASS benefit income and capital are not
        tested so the citizen should be eligible.
        """
        ec, mocked_on_passported_benefits, mocked_on_nass_benefits = self.create_a_dummy_citizen(
            is_category="immigration", is_passported=False, is_nass_benefits=True
        )

        self.assertTrue(ec.is_eligible())
        self.assertFalse(mocked_on_passported_benefits.called)
        self.assertTrue(mocked_on_nass_benefits.called)

    def test_nass_benefit_is_not_eligible_and_category_isnt_immigration_and_disposable_capital_is_above_limit(self):
        """
        TEST: If a citizen is not in the category immigration or considered in any category in this instance,
        if they have not qualified for NASS benefits and their disposable capital is above the set limit then they will
        not qualify for legal aid.
        """
        ec, mocked_on_passported_benefits, mocked_on_nass_benefits = self.create_a_dummy_citizen(
            is_category="not_immigration", is_passported=False, is_nass_benefits=False
        )

        ec.is_disposable_capital_eligible = mock.MagicMock(return_value=False)
        self.assertFalse(ec.is_eligible())
        self.assertFalse(mocked_on_passported_benefits.called)
        self.assertTrue(mocked_on_nass_benefits.called)

    def test_nass_benefit_is_not_eligible_and_category_isnt_immigration_and_disposable_income_is_above_limit(self):
        """
        TEST:  If a citizen is not in the category immigration or considered in any category in this instance,
        if they have not qualified for NASS benefits and their disposable income is above the set limit then they will
        not qualify for legal aid.
        """
        ec, mocked_on_passported_benefits, mocked_on_nass_benefits = self.create_a_dummy_citizen(
            is_category="not_immigration",
            is_passported=False,
            is_nass_benefits=False,
            is_disposable_capital=True,
            is_gross_income=True,
            is_disposable_income=False,
        )

        self.assertFalse(ec.is_eligible())
        self.assertTrue(ec.is_gross_income_eligible.called)
        self.assertFalse(mocked_on_passported_benefits.called)
        self.assertTrue(mocked_on_nass_benefits.called)
