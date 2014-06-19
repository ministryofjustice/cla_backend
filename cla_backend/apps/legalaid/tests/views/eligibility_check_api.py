import random
import copy
import uuid
import mock
from django.core.urlresolvers import reverse

from rest_framework import status

from eligibility_calculator.exceptions import PropertyExpectedException

from legalaid.models import Category, EligibilityCheck, Property, \
    Person, Income, Savings

from core.tests.mommy_utils import make_recipe

from cla_common.money_interval.models import MoneyInterval


mi_dict_generator = lambda x: {"interval_period": "per_month", "per_interval_value": x}


class EligibilityCheckAPIMixin(object):

    def setUp(self):
        super(EligibilityCheckAPIMixin, self).setUp()

        self.list_url = reverse('%s:eligibility_check-list' %  self.API_URL_NAMESPACE)
        self.check = make_recipe('legalaid.eligibility_check',
            category=make_recipe('legalaid.category'),
            notes=u'lorem ipsum',
            you=make_recipe('legalaid.person',
                            income=make_recipe('legalaid.income'),
                            savings=make_recipe('legalaid.savings'),
                            deductions=make_recipe('legalaid.deductions'))
        )
        self.detail_url = self.get_detail_url(self.check.reference)

    def get_http_authorization(self):
        return None

    def get_detail_url(self, check_ref):
        return reverse(
            '%s:eligibility_check-detail'  % self.API_URL_NAMESPACE, args=(),
            kwargs={'reference': unicode(check_ref)}
        )

    def get_is_eligible_url(self, reference):
        return reverse(
            '%s:eligibility_check-is-eligible' % self.API_URL_NAMESPACE,
            args=(),
            kwargs={'reference': unicode(reference)}
        )

    def assertEligibilityCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['reference',
             'category',
             'notes',
             'your_problem_notes',
             'property_set',
             'dependants_young',
             'dependants_old',
             'you',
             'partner',
             'has_partner',
             'on_passported_benefits',
             'on_nass_benefits',
             'is_you_or_your_partner_over_60']
        )

    def assertIncomeEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in ['self_employed']:
            self.assertEqual(getattr(obj, prop), data.get(prop))

        for prop in ['other_income', 'earnings',]:
            moneyInterval = getattr(obj, prop)
            self.assertEqual(moneyInterval.per_interval_value, data.get(prop)['per_interval_value'])
            self.assertEqual(moneyInterval.interval_period, data.get(prop)['interval_period'])

    def assertSavingsEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in [
            'bank_balance', 'investment_balance',
            'asset_balance', 'credit_balance'
        ]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

    def assertDeductionsEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in ['criminal_legalaid_contributions']:
            self.assertEqual(getattr(obj, prop), data.get(prop))

        for prop in ['income_tax', 'national_insurance', 'maintenance', 'childcare',
                     'mortgage', 'rent']:
            moneyInterval = getattr(obj, prop)
            self.assertEqual(moneyInterval.per_interval_value, data.get(prop)['per_interval_value'])
            self.assertEqual(moneyInterval.interval_period, data.get(prop)['interval_period'])

    def assertPersonEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
            return

        o_income = getattr(obj, 'income')
        d_income = data.get('income')
        self.assertIncomeEqual(d_income, o_income)

        o_savings = getattr(obj, 'savings')
        d_savings = data.get('savings')
        self.assertSavingsEqual(d_savings, o_savings)

        o_deductions = getattr(obj, 'deductions')
        d_deductions = data.get('deductions')
        self.assertDeductionsEqual(d_deductions, o_deductions)

    def assertEligibilityCheckEqual(self, data, check):
        self.assertEqual(data['reference'], unicode(check.reference))
        self.assertEqual(data['category'], check.category.code if check.category else None)
        self.assertEqual(data['your_problem_notes'], check.your_problem_notes)
        self.assertEqual(data['notes'], check.notes)
        self.assertEqual(len(data['property_set']), check.property_set.count())
        self.assertEqual(data['dependants_young'], check.dependants_young)
        self.assertEqual(data['dependants_old'], check.dependants_old)
        self.assertPersonEqual(data['you'], check.you)
        self.assertPersonEqual(data['partner'], check.partner)

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_get_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    # CREATE

    def test_create_no_data(self):
        """
        CREATE data is empty
        """
        response = self.client.post(
            self.list_url, data={}, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference']
            )
        )

    def test_create_basic_data(self):
        """
        CREATE data is not empty
        """
        make_recipe('legalaid.category')

        category = Category.objects.all()[0]
        data={
            'category': category.code,
            'your_problem_notes': 'lorem',
            'dependants_young': 2,
            'dependants_old': 3,
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'], category=category,
                your_problem_notes=data['your_problem_notes'],
                dependants_young=data['dependants_young'],
                dependants_old=data['dependants_old']
            )
        )

    def test_create_basic_data_with_extras(self):
        """
        CREATE data includes random values for fields:
            `has_partner`, `is_you_or_your_partner_over_60`, `on_passported_benefits`

            Where the possible values are: [`True`, `False`, `None`]
        """
        make_recipe('legalaid.category')

        category = Category.objects.all()[0]
        data= {
            'category': category.code,
            'your_problem_notes': 'lorem',
            'has_partner': random.choice([None, True, False]),
            'is_you_or_your_partner_over_60': random.choice([None, True, False]),
            'on_passported_benefits': random.choice([None, True, False])
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                category=category,
                your_problem_notes=data['your_problem_notes'],
                has_partner=data['has_partner'],
                is_you_or_your_partner_over_60=data['is_you_or_your_partner_over_60'],
                on_passported_benefits=data['on_passported_benefits'],
            )
        )

    def test_create_then_patch_category(self):
        """
        PATCHED category is applied
        """
        make_recipe('legalaid.category', _quantity=2)

        category = Category.objects.all()[0]
        category2 = Category.objects.all()[1]

        # CREATING FIRST
        data={
            'category': category.code,
            'your_problem_notes': 'lorem',
            'dependants_young': 2,
            'dependants_old': 3,
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # NOW PATCHING
        reference = response.data['reference']
        detail_url = self.get_detail_url(reference)

        data['category'] = category2.code
        patch_response = self.client.patch(
            detail_url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        self.assertEligibilityCheckResponseKeys(patch_response)
        self.assertEligibilityCheckEqual(patch_response.data,
            EligibilityCheck(
                reference=reference, category=category2,
                your_problem_notes=data['your_problem_notes'],
                dependants_young=data['dependants_young'],
                dependants_old=data['dependants_old'],
            )
        )

    def test_create_with_properties(self):
        """
        CREATE data with properties
        """
        data={
            'property_set': [
                {'value': 111, 'mortgage_left': 222, 'share': 33, 'disputed': True},
                {'value': 999, 'mortgage_left': 888, 'share': 77, 'disputed': False}
            ]
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertEqual(len(data['property_set']), 2)
        self.assertItemsEqual([p['value'] for p in response.data['property_set']], [111, 999])
        self.assertItemsEqual([p['mortgage_left'] for p in response.data['property_set']], [222, 888])
        self.assertItemsEqual([p['share'] for p in response.data['property_set']], [33, 77])
        self.assertItemsEqual([p['disputed'] for p in response.data['property_set']], [True, False])

    def _get_valid_post_data(self):
        data={
            'has_partner': True,
            'you': {
                'savings': {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400,
                },
                'income': {
                    "earnings": mi_dict_generator(500),
                    "other_income": mi_dict_generator(600),
                    "self_employed": True,
                },
                'deductions': {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(715),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(20),
                    "criminal_legalaid_contributions": 730
                },
            },
            'partner': {
                'savings': {
                    "bank_balance": 1000,
                    "investment_balance": 2000,
                    "asset_balance": 3000,
                    "credit_balance": 4000,
                    },
                'income': {
                    "earnings": mi_dict_generator(5000),
                    "other_income": mi_dict_generator(6000),
                    "self_employed": False
                },
                'deductions': {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(715),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(20),
                    "criminal_legalaid_contributions": 730
                },
            },
        }
        return data

    def test_create_with_finances(self):
        """
        CREATE data with finances
        """
        data = self._get_valid_post_data()
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertEligibilityCheckEqual(
            response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                you=Person.from_dict(data['you']),
                partner=Person.from_dict(data['partner'])
            )
        )

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.

        @see: notes in test_errors_masked_by_drf(..)
        """
        data={
            'category': -1,
            'your_problem_notes': 'a'*501,
            'property_set': [
                {'value': 111, 'mortgage_left': 222, 'share': 33, 'disputed': True},  # valid
                {'value': -1, 'mortgage_left': -1, 'share': -1, 'disputed': True},  # invalid
                {'value': 0, 'mortgage_left': 0, 'share': 101, 'disputed': True},  # invalid
            ],
            'dependants_young': -1,
            'dependants_old': -1,
            'you': {
                'savings': {
                    "bank_balance": -1,
                    "investment_balance": -1,
                    "asset_balance": -1,
                    "credit_balance": -1,
                },
                'income': {
                   "earnings": {"interval_period": "per_month", "per_interval_value": 0 },
                   "other_income": {"interval_period": "per_month", "per_interval_value": 0 },
                },
                'deductions': {
                    "income_tax": {"interval_period": "per_month", "per_interval_value": 0 },
                    "national_insurance": {"interval_period": "per_month", "per_interval_value": 0 },
                    "maintenance": {"interval_period": "per_month", "per_interval_value": 0 },
                    "childcare": {"interval_period": "per_month", "per_interval_value": 0 },
                    "mortgage": {"interval_period": "per_month", "per_interval_value": 0 },
                    "rent": {"interval_period": "per_month", "per_interval_value": 0 },
                    "criminal_legalaid_contributions": -1
                }
            },
            'partner': {
                'savings': {
                    "bank_balance": -1,
                    "investment_balance": -1,
                    "asset_balance": -1,
                    "credit_balance": -1,
                },
                'income': {
                   "earnings": {"interval_period": "per_month", "per_interval_value": 0 },
                   "other_income": {"interval_period": "per_month", "per_interval_value": 0 },
                },
                'deductions': {
                    "income_tax": {"interval_period": "per_month", "per_interval_value": 0 },
                    "national_insurance": {"interval_period": "per_month", "per_interval_value": 0 },
                    "maintenance": {"interval_period": "per_month", "per_interval_value": 0 },
                    "childcare": {"interval_period": "per_month", "per_interval_value": 0 },
                    "mortgage": {"interval_period": "per_month", "per_interval_value": 0 },
                    "rent": {"interval_period": "per_month", "per_interval_value": 0 },
                    "criminal_legalaid_contributions": -1
                }
            },
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data
        self.assertItemsEqual(
            errors.keys(),
            [
                'category', 'your_problem_notes',
                'property_set', 'dependants_young', 'dependants_old',
                'you', 'partner'
            ]
        )
        self.assertEqual(errors['category'], [u"Object with code=-1 does not exist."])
        self.assertEqual(errors['your_problem_notes'], [u'Ensure this value has at most 500 characters (it has 501).'])
        self.assertItemsEqual(errors['property_set'], [
            {},
            {
                'share': [u'Ensure this value is greater than or equal to 0.'],
                'value': [u'Ensure this value is greater than or equal to 0.'],
                'mortgage_left': [u'Ensure this value is greater than or equal to 0.']
            },
            {'share': [u'Ensure this value is less than or equal to 100.']}
        ])
        self.assertEqual(errors['dependants_young'], [u'Ensure this value is greater than or equal to 0.'])
        self.assertEqual(errors['dependants_old'], [u'Ensure this value is greater than or equal to 0.'])
        self.maxDiff =None
        self.assertItemsEqual(
            errors['you'],
            [
                {
                    'savings': [
                        {
                            'credit_balance': [u'Ensure this value is greater than or equal to 0.'],
                            'asset_balance': [u'Ensure this value is greater than or equal to 0.'],
                            'investment_balance': [u'Ensure this value is greater than or equal to 0.'],
                            'bank_balance': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    ],
                    'deductions': [
                        {
                            'criminal_legalaid_contributions': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    ]
                }
            ]
        )
        self.assertItemsEqual(
            errors['partner'],
            [
                {
                    'savings': [
                        {
                            'credit_balance': [u'Ensure this value is greater than or equal to 0.'],
                            'asset_balance': [u'Ensure this value is greater than or equal to 0.'],
                            'investment_balance': [u'Ensure this value is greater than or equal to 0.'],
                            'bank_balance': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    ],
                    'deductions': [
                        {
                            'criminal_legalaid_contributions': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    ]
                }
            ]
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
                'error': {'you': [{'income': [{'earnings': [u'Ensure this value is less than or equal to 9999999999.']}]}]},
                'data': {   "you" : { "income" : { "earnings":
                                                    {"interval_period": "per_month",
                                                     "per_interval_value": 9999999999+1,
                                    }}}
                        }
            },
            {
                'error': {'partner': [{'income': [{'earnings': [u'Ensure this value is less than or equal to 9999999999.']}]}]},
                'data': {   "partner" : { "income" : { "earnings":
                                                    {"interval_period": "per_month",
                                                     "per_interval_value": 9999999999+1,
                                    }}}
                        }
            },
        ]

        # MoneyInterval income fields
        for who in ['you', 'partner']:
            for field_name in ["income_tax", "national_insurance", "maintenance", "childcare",\
                               "mortgage", "rent"]:
                a = {
                    'error': { who: [{'deductions': [{field_name: [u'Ensure this value is less than or equal to 9999999999.']}]}]},
                    'data': { who : { "deductions" : { field_name: {"interval_period": "per_month","per_interval_value": 9999999999+1}
                                        }}
                            }
                }
                ERRORS_DATA.append(a)

        for error_data in ERRORS_DATA:
            data = copy.deepcopy(valid_data)
            EligibilityCheckAPIMixin.deep_update(data, error_data['data'])
            response = self.client.post(
                self.list_url, data, format='json',
                HTTP_AUTHORIZATION=self.get_http_authorization()
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertDictEqual(error_data['error'], response.data)

    def test_create_in_error(self):
        self._test_method_in_error('post', self.list_url)

    # GET OBJECT

    def test_get_not_found(self):
        """
        Invalid reference => 404
        """
        not_found_detail_url = self.get_detail_url(uuid.uuid4())

        response = self.client.get(
            not_found_detail_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_object(self):
        """
        GET should not return properties of other eligibility check objects
        """
        make_recipe('legalaid.property', eligibility_check=self.check, _quantity=4)

        # making extra properties
        make_recipe('legalaid.property', eligibility_check=self.check, _quantity=5)

        self.assertEqual(Property.objects.count(), 9)

        response = self.client.get(
            self.detail_url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEligibilityCheckResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)

    # PATCH

    def test_patch_no_data(self):
        """
        PATCH data is empty so the object shouldn't change
        """
        response = self.client.patch(
            self.detail_url, data={}, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)

    def test_patch_basic_data(self):
        """
        PATCH data is not empty so the object should change
        """
        category2 = make_recipe('legalaid.category')

        data={
            'reference': 'just-trying...', # reference should never change
            'category': category2.code,
            'your_problem_notes': 'ipsum lorem2',
            'dependants_young': None,
            'dependants_old': 10,
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # checking the changed properties
        self.check.category = category2
        self.check.your_problem_notes = data['your_problem_notes']
        self.check.dependants_young = data['dependants_young']
        self.check.dependants_old = data['dependants_old']
        self.assertEligibilityCheckEqual(response.data, self.check)

    def test_patch_properties(self):
        """
        PATCH should add/remove/change properties.
        """
        properties = make_recipe('legalaid.property', eligibility_check=self.check, _quantity=4, disputed=False)

        # making extra propertiesn not associated to this eligibility check
        make_recipe('legalaid.property', _quantity=5)

        self.assertEqual(self.check.property_set.count(), 4)

        # changing property with id == 1, removing all the others and adding
        # an extra one
        data={
            'property_set': [
                {'value': 111, 'mortgage_left': 222, 'share': 33, 'id': properties[0].id, 'disputed': True},
                {'value': 999, 'mortgage_left': 888, 'share': 77, 'disputed': True}
            ]
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # nothing should have changed here
        self.assertEligibilityCheckEqual(response.data, self.check)

        # properties should have changed. The new property should have id == 10
        self.assertEqual(len(response.data['property_set']), 2)

        property_ids = [p['id'] for p in response.data['property_set']]
        self.assertTrue(properties[0].id in property_ids)
        self.assertFalse(set([p.id for p in properties[1:]]).intersection(set(property_ids)))

        self.assertItemsEqual([p['value'] for p in response.data['property_set']], [111, 999])
        self.assertItemsEqual([p['mortgage_left'] for p in response.data['property_set']], [222, 888])
        self.assertItemsEqual([p['share'] for p in response.data['property_set']], [33, 77])
        self.assertItemsEqual([p['disputed'] for p in response.data['property_set']], [True, True])

        # checking the db just in case
        self.assertEqual(self.check.property_set.count(), 2)

    def test_patch_with_finances(self):
        """
        PATCH should change finances.
        """
        data={
            'you': {
                'income': {
                    "earnings": mi_dict_generator(500),
                    "other_income": mi_dict_generator(600),
                    "self_employed": True,
                },
                'savings': {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400
                },
                'deductions': {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(7150),
                    "mortgage": mi_dict_generator(700),
                    "rent": mi_dict_generator(100),
                    "criminal_legalaid_contributions": 730
                },
            },
            'partner': {
                'income': {
                    "earnings": mi_dict_generator(5000),
                    "other_income": mi_dict_generator(6000),
                    "self_employed": False
                },
                'savings': {
                    "bank_balance": 1000,
                    "investment_balance": 2000,
                    "asset_balance": 3000,
                    "credit_balance": 4000
                },
                'deductions': {
                    "income_tax": mi_dict_generator(6000),
                    "national_insurance": mi_dict_generator(1000),
                    "maintenance": mi_dict_generator(7100),
                    "childcare": mi_dict_generator(7150),
                    "mortgage": mi_dict_generator(7000),
                    "rent": mi_dict_generator(200),
                    "criminal_legalaid_contributions": 7300
                },
            },
        }
        response = self.client.patch(
            self.detail_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # finances props should have changed
        self.check.you = Person.from_dict(data['you'])
        self.check.partner = Person.from_dict(data['partner'])
        self.assertEligibilityCheckEqual(response.data, self.check)

    def test_patch_with_partial_finances(self):
        """
        PATCH should change only given finances fields whilst keeping the others.
        """
        # setting existing values that should NOT change after the patch
        existing_your_finances_values = {
            'savings':{
                'bank_balance': 0,
                'investment_balance': 0,
                'asset_balance': 0,
                'credit_balance': 0,
            },
            'income':{
                'earnings': MoneyInterval('per_month', pennies=2200),
                'other_income': MoneyInterval('per_month', pennies=0),
                'self_employed': False,
            },

        }

        self.check.you.income = Income(id=self.check.you.income.id, **existing_your_finances_values['income'])
        self.check.you.income.save()

        self.check.you.savings = Savings(id=self.check.you.savings.id, **existing_your_finances_values['savings'])
        self.check.you.savings.save()

        # new values that should change after the patch
        data={
            'you': {
                'deductions': {
                    "income_tax": mi_dict_generator(600),
                    "national_insurance": mi_dict_generator(100),
                    "maintenance": mi_dict_generator(710),
                    "childcare": mi_dict_generator(715),
                    "mortgage": mi_dict_generator(620),
                    "rent": mi_dict_generator(100),
                    "criminal_legalaid_contributions": 730
                }
            }
        }
        response = self.client.patch(
            self.detail_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only given finances props should have changed
        expected_your_finances_values = {'you': copy.deepcopy(existing_your_finances_values)}
        expected_your_finances_values['you'].update(data['you'])
        self.check.you = Person.from_dict(expected_your_finances_values['you'])

        self.assertEligibilityCheckEqual(response.data, self.check)

    def test_patch_in_error(self):
        self._test_method_in_error('patch', self.detail_url)

    def test_others_property_cannot_be_set(self):
        """
        other_property is assigned to another eligibility_check.

        We try to assign this other_property to our self.check.

        The endpoint should NOT change the other_property and our self.check.property_set
        should NOT point to other_property.
        """
        other_property = make_recipe('legalaid.property')
        data={
            'property_set': [
                {'value': 0, 'mortgage_left': 0, 'share': 0, 'id': other_property.pk, 'disputed': False}
            ]
        }
        response = self.client.patch(
            self.detail_url, data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['property_set'][0]['id'], other_property.pk)
        self.assertNotEqual(other_property.eligibility_check.pk, self.check.pk)

    # Just check that eligibility check endpoint responds
    # in a sensible way

    def test_eligibility_check_not_exists_is_eligible_fail(self):
        wrong_ref = uuid.uuid4()
        response = self.client.post(
            self.get_is_eligible_url(wrong_ref), data={}, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('core.viewsets.EligibilityChecker')
    def test_eligibility_check_is_eligible_pass(self, mocked_eligibility_checker):
        v = mocked_eligibility_checker()
        v.is_eligible.return_value = True
        response = self.client.post(
            self.get_is_eligible_url(self.check.reference),
            data={},
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_eligible'], 'yes')

    @mock.patch('core.viewsets.EligibilityChecker')
    def test_eligibility_check_is_eligible_fail(self, mocked_eligibility_checker):
        v = mocked_eligibility_checker()
        v.is_eligible.return_value = False
        response = self.client.post(
            self.get_is_eligible_url(self.check.reference),
            data={},
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_eligible'], 'no')

    @mock.patch('core.viewsets.EligibilityChecker')
    def test_eligibility_check_is_eligible_unknown(self, mocked_eligibility_checker):
        v = mocked_eligibility_checker()
        v.is_eligible.side_effect = PropertyExpectedException
        response = self.client.post(
            self.get_is_eligible_url(self.check.reference),
            data={},
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_eligible'], 'unknown')
