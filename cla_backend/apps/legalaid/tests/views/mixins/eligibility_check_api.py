import copy
import uuid
import mock
import random
from django.core.urlresolvers import reverse

from rest_framework import status

from legalaid.models import Category, EligibilityCheck, Property, Person, Income, Savings

from core.tests.test_base import SimpleResourceAPIMixin, NestedSimpleResourceAPIMixin
from core.tests.mommy_utils import make_recipe

from cla_common.money_interval.models import MoneyInterval
from cla_common.constants import SPECIFIC_BENEFITS


def mi_dict_generator(x):
    return {"interval_period": "per_month", "per_interval_value": x}


class EligibilityCheckAPIMixin(SimpleResourceAPIMixin):
    LOOKUP_KEY = "reference"
    API_URL_BASE_NAME = "eligibility_check"
    RESOURCE_RECIPE = "legalaid.eligibility_check"

    @property
    def response_keys(self):
        return [
            "reference",
            "category",
            "notes",
            "your_problem_notes",
            "property_set",
            "dependants_young",
            "dependants_old",
            "you",
            "partner",
            "has_partner",
            "on_passported_benefits",
            "specific_benefits",
            "disregards",
            "on_nass_benefits",
            "is_you_or_your_partner_over_60",
        ]

    def make_resource(self):
        return make_recipe(
            "legalaid.eligibility_check",
            category=make_recipe("legalaid.category"),
            notes=u"lorem ipsum",
            you=make_recipe(
                "legalaid.person",
                income=make_recipe("legalaid.income"),
                savings=make_recipe("legalaid.savings"),
                deductions=make_recipe("legalaid.deductions"),
            ),
        )

    def _update(self, ref, data):
        url = self.get_detail_url(unicode(ref))
        return self.client.patch(url, data=data, HTTP_AUTHORIZATION=self.get_http_authorization(), format="json")

    def get_reference_from_response(self, data):
        return data["reference"]

    def get_is_eligible_url(self, reference):
        return reverse(
            "%s:eligibility_check-is-eligible" % self.API_URL_NAMESPACE,
            args=(),
            kwargs={self.LOOKUP_KEY: unicode(reference)},
        )

    def assertIncomeEqual(self, data, obj, partner=False):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in ["self_employed"]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

        props = [
            "other_income",
            "self_employment_drawings",
            "benefits",
            "tax_credits",
            "maintenance_received",
            "pension",
            "earnings",
        ]
        if not partner:
            props.append("child_benefits")

        for prop in props:
            moneyInterval = getattr(obj, prop)
            self.assertNotEqual(moneyInterval, None, prop)
            self.assertEqual(moneyInterval.per_interval_value, data.get(prop)["per_interval_value"])
            self.assertEqual(moneyInterval.interval_period, data.get(prop)["interval_period"])

    def assertSavingsEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in ["bank_balance", "investment_balance", "asset_balance", "credit_balance"]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

    def assertDeductionsEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in ["criminal_legalaid_contributions"]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

        for prop in ["income_tax", "national_insurance", "maintenance", "childcare", "mortgage", "rent"]:
            moneyInterval = getattr(obj, prop)
            self.assertEqual(moneyInterval.per_interval_value, data.get(prop)["per_interval_value"])
            self.assertEqual(moneyInterval.interval_period, data.get(prop)["interval_period"])

    def assertPersonEqual(self, data, obj, partner=False):
        if data is None or obj is None:
            self.assertEqual(data, obj)
            return

        o_income = getattr(obj, "income")
        d_income = data.get("income")
        self.assertIncomeEqual(d_income, o_income, partner=partner)

        o_savings = getattr(obj, "savings")
        d_savings = data.get("savings")
        self.assertSavingsEqual(d_savings, o_savings)

        o_deductions = getattr(obj, "deductions")
        d_deductions = data.get("deductions")
        self.assertDeductionsEqual(d_deductions, o_deductions)

    def assertEligibilityCheckEqual(self, data, check):
        self.assertEqual(data["reference"], unicode(check.reference))
        self.assertEqual(data["category"], check.category.code if check.category else None)
        self.assertEqual(data["your_problem_notes"], check.your_problem_notes)
        self.assertEqual(data["notes"], check.notes)
        self.assertEqual(len(data["property_set"]), check.property_set.count())
        self.assertEqual(data["dependants_young"], check.dependants_young)
        self.assertEqual(data["dependants_old"], check.dependants_old)
        self.assertPersonEqual(data["you"], check.you)
        self.assertPersonEqual(data["partner"], check.partner, partner=True)
        self.assertSavingsEqual(data["disputed_savings"], check.disputed_savings)

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # LIST
        self._test_get_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)

        # DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    # CREATE

    def test_create_no_data(self):
        """
        CREATE data is empty
        """
        response = self._create()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertTrue(len(response.data["reference"]) > 30)
        self.assertEligibilityCheckEqual(response.data, EligibilityCheck(reference=response.data["reference"]))

    def test_create_basic_data(self):
        """
        CREATE data is not empty
        """
        make_recipe("legalaid.category")

        category = Category.objects.all()[0]
        data = {"category": category.code, "your_problem_notes": "lorem", "dependants_young": 2, "dependants_old": 3}
        response = self._create(data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertTrue(len(response.data["reference"]) > 30)
        self.assertEligibilityCheckEqual(
            response.data,
            EligibilityCheck(
                reference=response.data["reference"],
                category=category,
                your_problem_notes=data["your_problem_notes"],
                dependants_young=data["dependants_young"],
                dependants_old=data["dependants_old"],
            ),
        )

    def test_create_basic_data_with_extras(self):
        """
        CREATE data includes random values for fields:
            `has_partner`, `is_you_or_your_partner_over_60`, `on_passported_benefits`

            Where the possible values are: [`True`, `False`, `None`]
        """
        make_recipe("legalaid.category")

        category = Category.objects.all()[0]
        data = {
            "category": category.code,
            "your_problem_notes": "lorem",
            "has_partner": random.choice([None, True, False]),
            "is_you_or_your_partner_over_60": random.choice([None, True, False]),
            "on_passported_benefits": random.choice([None, True, False]),
            "specific_benefits": None,
            "disregards": None,
        }
        response = self._create(data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertTrue(len(response.data["reference"]) > 30)
        self.assertEligibilityCheckEqual(
            response.data,
            EligibilityCheck(
                reference=response.data["reference"],
                category=category,
                your_problem_notes=data["your_problem_notes"],
                has_partner=data["has_partner"],
                is_you_or_your_partner_over_60=data["is_you_or_your_partner_over_60"],
                on_passported_benefits=data["on_passported_benefits"],
                specific_benefits=None,
                disregards=None,
            ),
        )

    def test_create_then_patch_category(self):
        """
        PATCHED category is applied
        """
        make_recipe("legalaid.category", _quantity=2)

        category = Category.objects.all()[0]
        category2 = Category.objects.all()[1]

        # CREATING FIRST
        data = {"category": category.code, "your_problem_notes": "lorem", "dependants_young": 2, "dependants_old": 3}
        response = self._create(data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # NOW PATCHING
        reference = self.get_reference_from_response(response.data)

        data["category"] = category2.code
        patch_response = self._update(reference, data=data)

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        self.assertResponseKeys(patch_response)
        self.assertEligibilityCheckEqual(
            patch_response.data,
            EligibilityCheck(
                reference=response.data["reference"],
                category=category2,
                your_problem_notes=data["your_problem_notes"],
                dependants_young=data["dependants_young"],
                dependants_old=data["dependants_old"],
            ),
        )

    def test_create_with_properties(self):
        """
        CREATE data with properties
        """
        data = {
            "property_set": [
                {"value": 111, "mortgage_left": 222, "share": 33, "disputed": True, "main": True},
                {"value": 999, "mortgage_left": 888, "share": 77, "disputed": False, "main": False},
            ]
        }
        response = self._create(data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertEqual(len(data["property_set"]), 2)
        self.assertItemsEqual([p["value"] for p in response.data["property_set"]], [111, 999])
        self.assertItemsEqual([p["mortgage_left"] for p in response.data["property_set"]], [222, 888])
        self.assertItemsEqual([p["share"] for p in response.data["property_set"]], [33, 77])
        self.assertItemsEqual([p["disputed"] for p in response.data["property_set"]], [True, False])

    def test_create_with_more_main_properties_fails(self):
        data = {
            "property_set": [
                {"value": 111, "mortgage_left": 222, "share": 33, "disputed": True, "main": True},
                {"value": 999, "mortgage_left": 888, "share": 77, "disputed": False, "main": True},
            ]
        }
        response = self._create(data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {"property_set": [u"Only one main property allowed"]})

    def _get_valid_post_data(self):
        data = {
            "has_partner": True,
            "you": {
                "savings": {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400,
                },
                "income": {
                    "earnings": mi_dict_generator(500),
                    "self_employment_drawings": mi_dict_generator(501),
                    "child_benefits": mi_dict_generator(502),
                    "benefits": mi_dict_generator(503),
                    "tax_credits": mi_dict_generator(504),
                    "maintenance_received": mi_dict_generator(505),
                    "pension": mi_dict_generator(506),
                    "other_income": mi_dict_generator(600),
                    "self_employed": True,
                },
                "deductions": {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(715),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(20),
                    "criminal_legalaid_contributions": 730,
                },
            },
            "partner": {
                "savings": {
                    "bank_balance": 1000,
                    "investment_balance": 2000,
                    "asset_balance": 3000,
                    "credit_balance": 4000,
                },
                "income": {
                    "earnings": mi_dict_generator(5000),
                    "self_employment_drawings": mi_dict_generator(5001),
                    "benefits": mi_dict_generator(5003),
                    "tax_credits": mi_dict_generator(5004),
                    "maintenance_received": mi_dict_generator(5005),
                    "pension": mi_dict_generator(5006),
                    "other_income": mi_dict_generator(6000),
                    "self_employed": False,
                },
                "deductions": {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(715),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(20),
                    "criminal_legalaid_contributions": 730,
                },
            },
            "disputed_savings": {
                "bank_balance": 1111,
                "investment_balance": 2222,
                "asset_balance": 3333,
                "credit_balance": 4444,
            },
        }
        return data

    def test_create_with_finances(self):
        """
        CREATE data with finances
        """
        data = self._get_valid_post_data()
        response = self._create(data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertEligibilityCheckEqual(
            response.data,
            EligibilityCheck(
                reference=response.data["reference"],
                you=Person.from_dict(data["you"]),
                partner=Person.from_dict(data["partner"]),
                disputed_savings=Savings(
                    bank_balance=1111, investment_balance=2222, asset_balance=3333, credit_balance=4444
                ),
            ),
        )

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.

        @see: notes in test_errors_masked_by_drf(..)
        """
        data = {
            "category": -1,
            "your_problem_notes": "a" * 501,
            "property_set": [
                {"value": 111, "mortgage_left": 222, "share": 33, "disputed": True},  # valid
                {"value": -1, "mortgage_left": -1, "share": -1, "disputed": True},  # invalid
                {"value": 0, "mortgage_left": 0, "share": 101, "disputed": True},  # invalid
            ],
            "dependants_young": -1,
            "dependants_old": -1,
            "you": {
                "savings": {"bank_balance": -1, "investment_balance": -1, "asset_balance": -1, "credit_balance": -1},
                "income": {
                    "earnings": {"interval_period": "per_month", "per_interval_value": 0},
                    "self_employment_drawings": {"interval_period": "per_month", "per_interval_value": 0},
                    "child_benefits": {"interval_period": "per_month", "per_interval_value": 0},
                    "benefits": {"interval_period": "per_month", "per_interval_value": 0},
                    "tax_credits": {"interval_period": "per_month", "per_interval_value": 0},
                    "maintenance_received": {"interval_period": "per_month", "per_interval_value": 0},
                    "pension": {"interval_period": "per_month", "per_interval_value": 0},
                    "other_income": {"interval_period": "per_month", "per_interval_value": 0},
                },
                "deductions": {
                    "income_tax": {"interval_period": "per_month", "per_interval_value": 0},
                    "national_insurance": {"interval_period": "per_month", "per_interval_value": 0},
                    "maintenance": {"interval_period": "per_month", "per_interval_value": 0},
                    "childcare": {"interval_period": "per_month", "per_interval_value": 0},
                    "mortgage": {"interval_period": "per_month", "per_interval_value": 0},
                    "rent": {"interval_period": "per_month", "per_interval_value": 0},
                    "criminal_legalaid_contributions": -1,
                },
            },
            "partner": {
                "savings": {"bank_balance": -1, "investment_balance": -1, "asset_balance": -1, "credit_balance": -1},
                "income": {
                    "earnings": {"interval_period": "per_month", "per_interval_value": 0},
                    "self_employment_drawings": {"interval_period": "per_month", "per_interval_value": 0},
                    "benefits": {"interval_period": "per_month", "per_interval_value": 0},
                    "tax_credits": {"interval_period": "per_month", "per_interval_value": 0},
                    "maintenance_received": {"interval_period": "per_month", "per_interval_value": 0},
                    "pension": {"interval_period": "per_month", "per_interval_value": 0},
                    "other_income": {"interval_period": "per_month", "per_interval_value": 0},
                },
                "deductions": {
                    "income_tax": {"interval_period": "per_month", "per_interval_value": 0},
                    "national_insurance": {"interval_period": "per_month", "per_interval_value": 0},
                    "maintenance": {"interval_period": "per_month", "per_interval_value": 0},
                    "childcare": {"interval_period": "per_month", "per_interval_value": 0},
                    "mortgage": {"interval_period": "per_month", "per_interval_value": 0},
                    "rent": {"interval_period": "per_month", "per_interval_value": 0},
                    "criminal_legalaid_contributions": -1,
                },
            },
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data
        self.assertItemsEqual(
            errors.keys(),
            ["category", "your_problem_notes", "property_set", "dependants_young", "dependants_old", "you", "partner"],
        )
        self.assertEqual(errors["category"], [u"Object with code=-1 does not exist."])
        self.assertEqual(errors["your_problem_notes"], [u"Ensure this field has no more than 500 characters."])
        self.assertItemsEqual(
            errors["property_set"],
            [
                {},
                {
                    "share": [u"Ensure this value is greater than or equal to 0."],
                    "value": [u"Ensure this value is greater than or equal to 0."],
                    "mortgage_left": [u"Ensure this value is greater than or equal to 0."],
                },
                {"share": [u"Ensure this value is less than or equal to 100."]},
            ],
        )
        self.assertEqual(errors["dependants_young"], [u"Ensure this value is greater than or equal to 0."])
        self.assertEqual(errors["dependants_old"], [u"Ensure this value is greater than or equal to 0."])
        self.maxDiff = None
        self.assertItemsEqual(
            errors["you"],
            {
                "savings": [
                    {
                        "credit_balance": [u"Ensure this value is greater than or equal to 0."],
                        "asset_balance": [u"Ensure this value is greater than or equal to 0."],
                        "investment_balance": [u"Ensure this value is greater than or equal to 0."],
                        "bank_balance": [u"Ensure this value is greater than or equal to 0."],
                    }
                ],
                "deductions": [
                    {"criminal_legalaid_contributions": [u"Ensure this value is greater than or equal to 0."]}
                ],
            },
        )
        self.assertItemsEqual(
            errors["partner"],
            {
                "savings": [
                    {
                        "credit_balance": [u"Ensure this value is greater than or equal to 0."],
                        "asset_balance": [u"Ensure this value is greater than or equal to 0."],
                        "investment_balance": [u"Ensure this value is greater than or equal to 0."],
                        "bank_balance": [u"Ensure this value is greater than or equal to 0."],
                    }
                ],
                "deductions": [
                    {"criminal_legalaid_contributions": [u"Ensure this value is greater than or equal to 0."]}
                ],
            },
        )

    @classmethod
    def deep_update(cls, d, u):
        import collections

        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = EligibilityCheckAPIMixin.deep_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d

    def test_errors_masked_by_drf(self):
        """
        @see note in cla_backend/apps/call_centre/tests/api/test_eligibility_check_api.py
                     test_errors_masked_by_drf(self):
        """
        valid_data = self._get_valid_post_data()
        ERRORS_DATA = [
            {
                "error": {
                    "you": {
                        "income": {
                            "earnings": [u"Ensure this value is less than or equal to 9999999999."],
                            "self_employment_drawings": [u"Ensure this value is less than or equal to 9999999999."],
                            "child_benefits": [u"Ensure this value is less than or equal to 9999999999."],
                            "benefits": [u"Ensure this value is less than or equal to 9999999999."],
                            "tax_credits": [u"Ensure this value is less than or equal to 9999999999."],
                            "pension": [u"Ensure this value is less than or equal to 9999999999."],
                            "maintenance_received": [u"Ensure this value is less than or equal to 9999999999."],
                            "other_income": [u"Ensure this value is less than or equal to 9999999999."],
                        }
                    }
                },
                "data": {
                    "you": {
                        "income": {
                            "earnings": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "self_employment_drawings": {
                                "interval_period": "per_month",
                                "per_interval_value": 9999999999 + 1,
                            },
                            "child_benefits": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "benefits": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "tax_credits": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "maintenance_received": {
                                "interval_period": "per_month",
                                "per_interval_value": 9999999999 + 1,
                            },
                            "pension": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "other_income": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                        }
                    }
                },
            },
            {
                "error": {
                    "partner": {
                        "income": {
                            "earnings": [u"Ensure this value is less than or equal to 9999999999."],
                            "self_employment_drawings": [u"Ensure this value is less than or equal to 9999999999."],
                            "benefits": [u"Ensure this value is less than or equal to 9999999999."],
                            "tax_credits": [u"Ensure this value is less than or equal to 9999999999."],
                            "pension": [u"Ensure this value is less than or equal to 9999999999."],
                            "maintenance_received": [u"Ensure this value is less than or equal to 9999999999."],
                            "other_income": [u"Ensure this value is less than or equal to 9999999999."],
                        }
                    }
                },
                "data": {
                    "partner": {
                        "income": {
                            "earnings": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "self_employment_drawings": {
                                "interval_period": "per_month",
                                "per_interval_value": 9999999999 + 1,
                            },
                            "benefits": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "tax_credits": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "maintenance_received": {
                                "interval_period": "per_month",
                                "per_interval_value": 9999999999 + 1,
                            },
                            "pension": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                            "other_income": {"interval_period": "per_month", "per_interval_value": 9999999999 + 1},
                        }
                    }
                },
            },
        ]

        # MoneyInterval income fields
        for who in ["you", "partner"]:
            for field_name in ["income_tax", "national_insurance", "maintenance", "childcare", "mortgage", "rent"]:
                a = {
                    "error": {
                        who: {"deductions": {field_name: [u"Ensure this value is less than or equal to 9999999999."]}}
                    },
                    "data": {
                        who: {
                            "deductions": {
                                field_name: {"interval_period": "per_month", "per_interval_value": 9999999999 + 1}
                            }
                        }
                    },
                }
                ERRORS_DATA.append(a)

        for error_data in ERRORS_DATA:
            data = copy.deepcopy(valid_data)
            EligibilityCheckAPIMixin.deep_update(data, error_data["data"])

            response = self._create(data=data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertDictEqual(error_data["error"], response.data)

    def test_create_in_error(self):
        if hasattr(self, "list_url") and self.list_url:
            self._test_method_in_error("post", self.list_url)

    # GET OBJECT

    def test_get_not_found(self):
        """
        Invalid reference => 404
        """
        not_found_detail_url = self.get_detail_url(uuid.uuid4())

        response = self.client.get(
            not_found_detail_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_object(self):
        """
        GET should not return properties of other eligibility check objects
        """
        make_recipe("legalaid.property", eligibility_check=self.resource, _quantity=4)

        # making extra properties
        make_recipe("legalaid.property", eligibility_check=self.resource, _quantity=5)

        self.assertEqual(Property.objects.count(), 9)

        response = self.client.get(self.detail_url, format="json", HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.resource)

    # PATCH

    def test_patch_no_data(self):
        """
        PATCH data is empty so the object shouldn't change
        """
        response = self.client.patch(
            self.detail_url, data={}, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.resource)

    def test_patch_basic_data(self):
        """
        PATCH data is not empty so the object should change
        """
        category2 = make_recipe("legalaid.category")

        data = {
            "reference": "just-trying...",  # reference should never change
            "category": category2.code,
            "your_problem_notes": "ipsum lorem2",
            "dependants_young": None,
            "dependants_old": 10,
        }
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking the changed properties
        self.resource.category = category2
        self.resource.your_problem_notes = data["your_problem_notes"]
        self.resource.dependants_young = data["dependants_young"]
        self.resource.dependants_old = data["dependants_old"]
        self.assertEligibilityCheckEqual(response.data, self.resource)

    def test_patch_specific_benefits(self):
        # with specific_benefits == True
        data = {
            "on_passported_benefits": True,
            "specific_benefits": {
                SPECIFIC_BENEFITS.UNIVERSAL_CREDIT: False,
                SPECIFIC_BENEFITS.INCOME_SUPPORT: True,
                SPECIFIC_BENEFITS.PENSION_CREDIT: True,
            },
        }
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["on_passported_benefits"], data["on_passported_benefits"])
        self.assertEqual(response.data["specific_benefits"], data["specific_benefits"])

        # with on_passported_benefits == False and specific_benefits == {}
        data = {"on_passported_benefits": False, "specific_benefits": {}}
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["on_passported_benefits"], data["on_passported_benefits"])
        self.assertEqual(response.data["specific_benefits"], {})

        # with on_passported_benefits == True and specific_benefits == None
        #   => should keep the same values
        data = {"on_passported_benefits": True, "specific_benefits": None}
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["on_passported_benefits"], data["on_passported_benefits"])
        self.assertEqual(response.data["specific_benefits"], None)

    def test_patch_properties(self):
        """
        PATCH should add/remove/change properties.
        """
        properties = make_recipe("legalaid.property", eligibility_check=self.resource, _quantity=4, disputed=False)

        # making extra properties not associated to this eligibility check
        make_recipe("legalaid.property", _quantity=5)

        self.assertEqual(self.resource.property_set.count(), 4)

        # changing property with id == 1, removing all the others and adding
        # an extra one
        data = {
            "property_set": [
                {"value": 111, "mortgage_left": 222, "share": 33, "id": properties[0].id, "disputed": True},
                {"value": 999, "mortgage_left": 888, "share": 77, "disputed": True},
            ]
        }
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # nothing should have changed here
        self.assertEligibilityCheckEqual(response.data, self.resource)

        # properties should have changed. The new property should have id == 10
        self.assertEqual(len(response.data["property_set"]), 2)

        property_ids = [p["id"] for p in response.data["property_set"]]
        self.assertTrue(properties[0].id in property_ids)
        self.assertFalse(set([p.id for p in properties[1:]]).intersection(set(property_ids)))

        self.assertItemsEqual([p["value"] for p in response.data["property_set"]], [111, 999])
        self.assertItemsEqual([p["mortgage_left"] for p in response.data["property_set"]], [222, 888])
        self.assertItemsEqual([p["share"] for p in response.data["property_set"]], [33, 77])
        self.assertItemsEqual([p["disputed"] for p in response.data["property_set"]], [True, True])

        # checking the db just in case
        self.assertEqual(self.resource.property_set.count(), 2)
        # make sure did not delete all properties by accident
        self.assertEqual(Property.objects.all().count(), 7)

    def test_delete_all_properties(self):
        """
        PATCH should remove all properties.
        """
        make_recipe("legalaid.property", eligibility_check=self.resource, _quantity=4, disputed=False)

        # making extra properties not associated to this eligibility check
        make_recipe("legalaid.property", _quantity=5)

        self.assertEqual(self.resource.property_set.count(), 4)
        # remove all properties
        data = {"property_set": []}
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # nothing should have changed here
        self.assertEligibilityCheckEqual(response.data, self.resource)

        # check eligibility check has zero properties
        self.assertEqual(EligibilityCheck.objects.get(pk=self.resource.pk).property_set.count(), 0)

        # properties should have changed. Response should have no properties
        self.assertEqual(len(response.data["property_set"]), 0)

    def test_patch_with_finances(self):
        """
        PATCH should change finances.
        """
        data = {
            "you": {
                "income": {
                    "earnings": mi_dict_generator(500),
                    "self_employment_drawings": mi_dict_generator(501),
                    "child_benefits": mi_dict_generator(502),
                    "benefits": mi_dict_generator(503),
                    "tax_credits": mi_dict_generator(504),
                    "maintenance_received": mi_dict_generator(505),
                    "pension": mi_dict_generator(506),
                    "other_income": mi_dict_generator(600),
                    "self_employed": True,
                },
                "savings": {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400,
                },
                "deductions": {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(7150),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(100),
                    "criminal_legalaid_contributions": 730,
                },
            },
            "partner": {
                "income": {
                    "earnings": mi_dict_generator(5000),
                    "self_employment_drawings": mi_dict_generator(5001),
                    "child_benefits": mi_dict_generator(5002),
                    "benefits": mi_dict_generator(5003),
                    "tax_credits": mi_dict_generator(5004),
                    "maintenance_received": mi_dict_generator(5005),
                    "pension": mi_dict_generator(5006),
                    "other_income": mi_dict_generator(6000),
                    "self_employed": False,
                },
                "savings": {
                    "bank_balance": 1000,
                    "investment_balance": 2000,
                    "asset_balance": 3000,
                    "credit_balance": 4000,
                },
                "deductions": {
                    "income_tax": mi_dict_generator(6000),
                    "national_insurance": mi_dict_generator(1000),
                    "maintenance": mi_dict_generator(7100),
                    "childcare": mi_dict_generator(7150),
                    "mortgage": mi_dict_generator(7000),
                    "rent": mi_dict_generator(200),
                    "criminal_legalaid_contributions": 7300,
                },
            },
        }
        response = self.client.patch(
            self.detail_url, data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # finances props should have changed
        self.resource.you = Person.from_dict(data["you"])
        self.resource.partner = Person.from_dict(data["partner"])
        self.assertEligibilityCheckEqual(response.data, self.resource)

        self.assertTrue("child_benefits" in response.data["you"]["income"].keys())
        self.assertTrue("child_benefits" not in response.data["partner"]["income"].keys())

    def test_patch_with_partial_finances(self):
        """
        PATCH should change only given finances fields whilst keeping the others.
        """
        # setting existing values that should NOT change after the patch
        existing_your_finances_values = {
            "savings": {"bank_balance": 0, "investment_balance": 0, "asset_balance": 0, "credit_balance": 0},
            "income": {
                "earnings": MoneyInterval("per_month", pennies=2200),
                "self_employment_drawings": MoneyInterval("per_month", pennies=2201),
                "child_benefits": MoneyInterval("per_month", pennies=2202),
                "benefits": MoneyInterval("per_month", pennies=2203),
                "tax_credits": MoneyInterval("per_month", pennies=2204),
                "maintenance_received": MoneyInterval("per_month", pennies=2205),
                "pension": MoneyInterval("per_month", pennies=2206),
                "other_income": MoneyInterval("per_month", pennies=0),
                "self_employed": False,
            },
        }

        self.resource.you.income = Income(id=self.resource.you.income.id, **existing_your_finances_values["income"])
        self.resource.you.income.save()

        self.resource.you.savings = Savings(
            id=self.resource.you.savings.id, **existing_your_finances_values["savings"]
        )
        self.resource.you.savings.save()

        # new values that should change after the patch
        data = {
            "you": {
                "deductions": {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(715),
                    "mortgage": mi_dict_generator(620),
                    "rent": mi_dict_generator(100),
                    "criminal_legalaid_contributions": 730,
                }
            }
        }
        response = self.client.patch(
            self.detail_url, data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only given finances props should have changed
        expected_your_finances_values = {"you": copy.deepcopy(existing_your_finances_values)}
        expected_your_finances_values["you"].update(data["you"])
        self.resource.you = Person.from_dict(expected_your_finances_values["you"])

        self.assertEligibilityCheckEqual(response.data, self.resource)

    def test_patch_with_no_partner_finances(self):
        """
        PATCH should change finances.
        """
        data = {
            "you": {
                "income": {
                    "earnings": mi_dict_generator(500),
                    "self_employment_drawings": mi_dict_generator(501),
                    "child_benefits": mi_dict_generator(502),
                    "benefits": mi_dict_generator(503),
                    "tax_credits": mi_dict_generator(504),
                    "maintenance_received": mi_dict_generator(505),
                    "pension": mi_dict_generator(506),
                    "other_income": mi_dict_generator(600),
                    "self_employed": True,
                },
                "savings": {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400,
                },
                "deductions": {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(7150),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(100),
                    "criminal_legalaid_contributions": 730,
                },
            },
            "partner": {
                "income": {
                    "earnings": mi_dict_generator(5000),
                    "self_employment_drawings": mi_dict_generator(5001),
                    "child_benefits": mi_dict_generator(5002),
                    "benefits": mi_dict_generator(5003),
                    "tax_credits": mi_dict_generator(5004),
                    "maintenance_received": mi_dict_generator(5005),
                    "pension": mi_dict_generator(5006),
                    "other_income": mi_dict_generator(6000),
                    "self_employed": False,
                },
                "savings": None,
                "deductions": None,
            },
        }
        response = self.client.patch(
            self.detail_url, data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_with_no_partner_income(self):
        """
        PATCH should change finances.
        """
        data = {
            "you": {
                "income": {
                    "earnings": mi_dict_generator(500),
                    "self_employment_drawings": mi_dict_generator(501),
                    "child_benefits": mi_dict_generator(502),
                    "benefits": mi_dict_generator(503),
                    "tax_credits": mi_dict_generator(504),
                    "maintenance_received": mi_dict_generator(505),
                    "pension": mi_dict_generator(506),
                    "other_income": mi_dict_generator(600),
                    "self_employed": True,
                },
                "savings": {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400,
                },
                "deductions": {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(7150),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(100),
                    "criminal_legalaid_contributions": 730,
                },
            },
            "partner": {
                "income": {
                    "earnings": None,
                    "self_employment_drawings": None,
                    "child_benefits": None,
                    "benefits": None,
                    "tax_credits": None,
                    "maintenance_received": None,
                    "pension": None,
                    "other_income": None,
                    "self_employed": True,
                },
                "savings": None,
                "deductions": None,
            },
        }
        response = self.client.patch(
            self.detail_url, data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_null_partner_self_employed(self):
        """
        The elegibility check should still return 200 even when the partner object has
        their self employment status set to 'None', such as when the client has no partner.
        """
        data = {
            "you": {
                "income": {
                    "earnings": mi_dict_generator(500),
                    "self_employment_drawings": mi_dict_generator(501),
                    "child_benefits": mi_dict_generator(502),
                    "benefits": mi_dict_generator(503),
                    "tax_credits": mi_dict_generator(504),
                    "maintenance_received": mi_dict_generator(505),
                    "pension": mi_dict_generator(506),
                    "other_income": mi_dict_generator(600),
                    "self_employed": True,
                },
                "savings": {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400,
                },
                "deductions": {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(7150),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(100),
                    "criminal_legalaid_contributions": 730,
                },
            },
            "partner": {
                "income": {
                    "earnings": None,
                    "self_employment_drawings": None,
                    "child_benefits": None,
                    "benefits": None,
                    "tax_credits": None,
                    "maintenance_received": None,
                    "pension": None,
                    "other_income": None,
                    "self_employed": None,
                },
                "savings": {},
                "deductions": {},
            },
        }
        response = self.client.patch(
            self.detail_url, data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_in_error(self):
        self._test_method_in_error("patch", self.detail_url)

    def test_others_property_cannot_be_set(self):
        """
        other_property is assigned to another eligibility_check.

        We try to assign this other_property to our self.resource.

        The endpoint should NOT change the other_property and our self.resource.property_set
        should NOT point to other_property.
        """
        other_property = make_recipe("legalaid.property")
        data = {
            "property_set": [{"value": 0, "mortgage_left": 0, "share": 0, "id": other_property.pk, "disputed": False}]
        }
        response = self.client.patch(
            self.detail_url, data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["property_set"][0]["id"], other_property.pk)
        self.assertNotEqual(other_property.eligibility_check.pk, self.resource.pk)

    # Just check that eligibility check endpoint responds
    # in a sensible way

    def test_eligibility_check_not_exists_is_eligible_fail(self):
        wrong_ref = uuid.uuid4()
        response = self.client.post(
            self.get_is_eligible_url(wrong_ref),
            data={},
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch("legalaid.models.EligibilityChecker")
    def test_eligibility_check_is_eligible_pass(self, mocked_eligibility_checker):
        v = mocked_eligibility_checker()
        v.is_eligible_with_reasons.return_value = ("yes", True, True, True)
        response = self.client.post(
            self.get_is_eligible_url(self.resource_lookup_value),
            data={},
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_eligible"], "yes")

    @mock.patch("legalaid.models.EligibilityChecker")
    def test_eligibility_check_is_eligible_fail(self, mocked_eligibility_checker):
        v = mocked_eligibility_checker()
        v.is_eligible_with_reasons.return_value = ("no", None, None, None)
        response = self.client.post(
            self.get_is_eligible_url(self.resource_lookup_value),
            data={},
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_eligible"], "no")

    @mock.patch("legalaid.models.EligibilityChecker")
    def test_eligibility_check_is_eligible_unknown(self, mocked_eligibility_checker):
        v = mocked_eligibility_checker()
        v.is_eligible_with_reasons.return_value = ("unknown", None, None, None)
        response = self.client.post(
            self.get_is_eligible_url(self.resource_lookup_value),
            data={},
            format="json",
            HTTP_AUTHORIZATION=self.get_http_authorization(),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_eligible"], "unknown")

    def test_eligibility_check_under_18(self):
        from cla_common.constants import ELIGIBILITY_STATES

        state, ec, reasons = self.resource.get_eligibility_state()
        self.assertEqual(state, ELIGIBILITY_STATES.UNKNOWN)
        data = {"is_you_under_18": True, "under_18_passported": True}
        response = self.client.patch(
            self.detail_url, data=data, format="json", HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.data["state"], ELIGIBILITY_STATES.YES)


class NestedEligibilityCheckAPIMixin(NestedSimpleResourceAPIMixin, EligibilityCheckAPIMixin):
    LOOKUP_KEY = "case_reference"
    PARENT_LOOKUP_KEY = "reference"
    PARENT_RESOURCE_RECIPE = "legalaid.case"
    PK_FIELD = "eligibility_check"

    def get_reference_from_response(self, data):
        return self.parent_resource.reference

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # DETAIL
        self._test_delete_not_allowed(self.detail_url)
