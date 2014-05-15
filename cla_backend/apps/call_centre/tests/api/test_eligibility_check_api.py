import copy
import uuid
import mock
from model_mommy import mommy

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from eligibility_calculator.exceptions import PropertyExpectedException
from legalaid.models import Category, EligibilityCheck, Property, \
    Person, Income, Savings

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin

from call_centre.serializers import EligibilityCheckSerializer


def make_recipe(model_name, **kwargs):
    return mommy.make_recipe('legalaid.tests.%s' % model_name, **kwargs)


class EligibilityCheckTests(CLAOperatorAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(EligibilityCheckTests, self).setUp()

        self.list_url = reverse('call_centre:eligibility_check-list')
        self.check = make_recipe('eligibility_check',
            category=make_recipe('category'),
            notes=u'lorem ipsum',
            you=make_recipe('person',
                            income=make_recipe('income'),
                            savings=make_recipe('savings'),
                            deductions=make_recipe('deductions'))
        )
        self.detail_url = reverse(
            'call_centre:eligibility_check-detail', args=(),
            kwargs={'reference': unicode(self.check.reference)}
        )

    def get_is_eligible_url(self, reference):
        return reverse(
            'call_centre:eligibility_check-is-eligible',
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
             'is_you_or_your_partner_over_60',
             'state'
            ]
        )

    def assertIncomeEqual(self, data, obj):
        if obj is None or data is None:
            self.assertEqual(obj, data)
            return

        for prop in [
             'earnings', 'other_income', 'self_employed'
        ]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

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

        for prop in [
            'income_tax_and_ni', 'maintenance', 'childcare',
            'mortgage_or_rent', 'criminal_legalaid_contributions'
        ]:
            self.assertEqual(getattr(obj, prop), data.get(prop))

    def assertFinanceEqual(self, data, obj):
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
        self.assertFinanceEqual(data['you'], check.you)
        self.assertFinanceEqual(data['partner'], check.partner)

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

    def test_methods_not_authorized(self):
        ### LIST
        self._test_post_not_authorized(self.list_url, self.staff_token)
        self._test_put_not_authorized(self.list_url, self.staff_token)
        self._test_delete_not_authorized(self.list_url, self.staff_token)

        ### DETAIL
        self._test_post_not_authorized(self.detail_url, self.staff_token)
        self._test_delete_not_authorized(self.detail_url, self.staff_token)


    # CREATE

    def test_create_no_data(self):
        """
        CREATE data is empty
        """
        response = self.client.post(
            self.list_url, data={}, format='json',
        HTTP_AUTHORIZATION='Bearer %s' % self.token)
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
        make_recipe('category')

        category = Category.objects.all()[0]
        data={
            'category': category.code,
            'your_problem_notes': 'lorem',
            'dependants_young': 2,
            'dependants_old': 3,
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                category=category,
                your_problem_notes=data['your_problem_notes'],
                dependants_young=2, dependants_old=3
            )
        )

    def test_create_basic_data_with_partner(self):
        """
        CREATE data includes `has_partner`
        """
        make_recipe('category')

        category = Category.objects.all()[0]
        data={
            'category': category.code,
            'your_problem_notes': 'lorem',
            'has_partner': True
            }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                category=category,
                your_problem_notes=data['your_problem_notes'],
                has_partner=data['has_partner']
            )
        )

    def test_create_basic_data_with_over_60(self):
        """
        CREATE data includes over 60
        """
        make_recipe('category')

        category = Category.objects.all()[0]
        data={
            'category': category.code,
            'your_problem_notes': 'lorem',
            'is_you_or_your_partner_over_60': True
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                category=category,
                your_problem_notes=data['your_problem_notes'],
                is_you_or_your_partner_over_60=data['is_you_or_your_partner_over_60']
            )
        )

    def test_create_basic_data_with_on_benefits(self):
        """
        CREATE data includes `on_passported_benefits`
        """
        make_recipe('category')

        category = Category.objects.all()[0]
        data={
            'category': category.code,
            'your_problem_notes': 'lorem',
            'on_passported_benefits': True
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                category=category,
                your_problem_notes=data['your_problem_notes'],
                on_passported_benefits=data['on_passported_benefits'],
            )
        )

    def test_create_then_patch_category(self):
        """
        PATCHED category is applied
        """
        make_recipe('category', _quantity=2)

        category = Category.objects.all()[0]
        category2 = Category.objects.all()[1]

        data={
            'category': category.code,
            'your_problem_notes': 'lorem',
            'dependants_young': 2,
            'dependants_old': 3,
            }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                category=category,
                your_problem_notes=data['your_problem_notes'],
                dependants_young=2, dependants_old=3
            )
        )

        data['category'] = category2.code
        response2 = self.client.patch(
            self.detail_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)

        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertEligibilityCheckResponseKeys(response2)
        self.assertEqual(response2.data['category'], category2.code)

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
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEqual(response.data['category'], None)
        self.assertEqual(response.data['notes'], '')
        self.assertEqual(len(response.data['property_set']), 2)
        self.assertEqual(response.data['dependants_young'], 0)
        self.assertEqual(response.data['dependants_old'], 0)
        self.assertEqual(len(response.data['property_set']), 2)
        self.assertItemsEqual([p['value'] for p in response.data['property_set']], [111, 999])
        self.assertItemsEqual([p['mortgage_left'] for p in response.data['property_set']], [222, 888])
        self.assertItemsEqual([p['share'] for p in response.data['property_set']], [33, 77])
        self.assertItemsEqual([p['disputed'] for p in response.data['property_set']], [True, False])

    def test_create_with_finances(self):
        """
        CREATE data with finances
        """
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
                    "earnings": 500,
                    "other_income": 600,
                    "self_employed": True,
                },
                'deductions': {
                    "income_tax_and_ni": 700,
                    "maintenance": 710,
                    "childcare": 715,
                    "mortgage_or_rent": 720,
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
                    "earnings": 5000,
                    "other_income": 6000,
                    "self_employed": False
                },

            },
        }
        response = self.client.post(
            self.list_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
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
        """
        data={
            'state': 0,
            'category': -1,
            'notes': 'a'*501,
            'your_problem_notes': 'a'*501,
            'property_set': [
                {'value': 111, 'mortgage_left': 222, 'share': 33, 'disputed': True},  # valid
                {'value': -1, 'mortgage_left': -1, 'share': -1, 'disputed': False},  # invalid
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
                    "earnings": -1,
                    "other_income": -1,
                },
                'deductions': {
                    "income_tax_and_ni": -1,
                    "maintenance": -1,
                    "childcare": -1,
                    "mortgage_or_rent": -1,
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
                    "earnings": -1,
                    "other_income": -1
                },
                'deductions': {
                    "income_tax_and_ni": -1,
                    "maintenance": -1,
                    "childcare": -1,
                    "mortgage_or_rent": -1,
                    "criminal_legalaid_contributions": -1
                }
            },
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
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
                    'income': [
                        {
                            'earnings': [u'Ensure this value is greater than or equal to 0.'],
                            'other_income': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    ],
                    'deductions': [
                        {
                            'income_tax_and_ni': [u'Ensure this value is greater than or equal to 0.'],
                            'maintenance': [u'Ensure this value is greater than or equal to 0.'],
                            'childcare': [u'Ensure this value is greater than or equal to 0.'],
                            'mortgage_or_rent': [u'Ensure this value is greater than or equal to 0.'],
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
                    'income': [
                        {
                            'earnings': [u'Ensure this value is greater than or equal to 0.'],
                            'other_income': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    ],
                    'deductions': [
                        {
                            'income_tax_and_ni': [u'Ensure this value is greater than or equal to 0.'],
                            'maintenance': [u'Ensure this value is greater than or equal to 0.'],
                            'childcare': [u'Ensure this value is greater than or equal to 0.'],
                            'mortgage_or_rent': [u'Ensure this value is greater than or equal to 0.'],
                            'criminal_legalaid_contributions': [u'Ensure this value is greater than or equal to 0.'],
                        }
                    ]
                }
            ]
        )

    def test_create_in_error(self):
        self._test_method_in_error('post', self.list_url)

    # GET OBJECT

    def test_get_not_found(self):
        """
        Invalid reference => 404
        """
        not_found_detail_url = reverse(
            'call_centre:eligibility_check-detail', args=(),
            kwargs={'reference': uuid.uuid4()}
        )

        response = self.client.get(not_found_detail_url, format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_object(self):
        """
        GET should not return properties of other eligibility check objects
        """
        make_recipe('property', eligibility_check=self.check, _quantity=4)

        # making extra properties
        make_recipe('property', eligibility_check=self.check, _quantity=5)

        self.assertEqual(Property.objects.count(), 9)

        response = self.client.get(self.detail_url, format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEligibilityCheckResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)

    # PATCH

    def test_patch_no_data(self):
        """
        PATCH data is empty so the object shouldn't change
        """
        response = self.client.patch(
            self.detail_url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEligibilityCheckResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)

    def test_patch_basic_data(self):
        """
        PATCH data is not empty so the object should change
        """
        category2 = make_recipe('category')

        data={
            'reference': 'just-trying...', # reference should never change
            'category': category2.code,
            'your_problem_notes': 'ipsum lorem2',
            'dependants_young': 10,
            'dependants_old': 10,
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
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
        properties = make_recipe('property', eligibility_check=self.check, _quantity=4)

        # making extra properties
        make_recipe('property', _quantity=5, disputed=False)

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
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # nothing should have changed here
        self.assertEqual(response.data['reference'], unicode(self.check.reference))
        self.assertEqual(response.data['category'], self.check.category.code)
        self.assertEqual(response.data['notes'], self.check.notes)
        self.assertEqual(response.data['dependants_young'], self.check.dependants_young)
        self.assertEqual(response.data['dependants_old'], self.check.dependants_old)

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
                    "earnings": 500,
                    "other_income": 600,
                    "self_employed": True,
                },
                'savings': {
                    "bank_balance": 100,
                    "investment_balance": 200,
                    "asset_balance": 300,
                    "credit_balance": 400,
                },
                'deductions': {
                    "income_tax_and_ni": 700,
                    "maintenance": 710,
                    "childcare": 715,
                    "mortgage_or_rent": 720,
                    "criminal_legalaid_contributions": 730
                },
            },
            'partner': {
                'income': {
                    "earnings": 5000,
                    "other_income": 6000,
                    "self_employed": False
                },
                'savings': {
                    "bank_balance": 1000,
                    "investment_balance": 2000,
                    "asset_balance": 3000,
                    "credit_balance": 4000,
                },
                'deductions': {
                    "income_tax_and_ni": 7000,
                    "maintenance": 7100,
                    "childcare": 7150,
                    "mortgage_or_rent": 7200,
                    "criminal_legalaid_contributions": 7300
                },
            },
        }
        response = self.client.patch(
            self.detail_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
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
                'earnings': 0,
                'other_income': 0,
                'self_employed': False,
            },

        }

        self.check.you.income = Income(**existing_your_finances_values['income'])
        self.check.you.income.save()

        self.check.you.savings = Savings(**existing_your_finances_values['savings'])
        self.check.you.savings.save()

        # new values that should change after the patch
        data={
            'you': {
                'deductions': {
                    "income_tax_and_ni": 700,
                    "maintenance": 710,
                    "childcare": 715,
                    "mortgage_or_rent": 720,
                    "criminal_legalaid_contributions": 730
                }
            }
        }
        response = self.client.patch(
            self.detail_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only given finances props should have changed
        expected_your_finances_values = {'you': copy.deepcopy(existing_your_finances_values)}
        expected_your_finances_values['you'].update(data['you'])
        self.check.you = Person.from_dict(expected_your_finances_values['you'])

        self.assertEligibilityCheckEqual(response.data, self.check)

    def test_patch_with_partial_law_category(self):
        """
        PATCH should change only given category.
        """
        initial = EligibilityCheckSerializer(instance=self.check).data
        # existing values that should NOT change after the patch
        categories = mommy.make_recipe('legalaid.tests.category', _quantity=3)
        # new values that should change after the patch
        data={
            'category': categories[1].code
        }
        response = self.client.patch(
            self.detail_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only given category prop should have changed
        self.check.category = categories[1]
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
        other_property = make_recipe('property', disputed=True)
        data={
            'property_set': [
                {'value': 0, 'mortgage_left': 0, 'share': 0, 'id': other_property.pk, 'disputed': False}
            ]
        }
        response = self.client.patch(
            self.detail_url, data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['property_set'][0]['id'], other_property.pk)
        self.assertNotEqual(other_property.eligibility_check.pk, self.check.pk)

    # PUT

    def test_put_basic_data(self):
        """
        PUT should override the values
        """
        make_recipe('property', eligibility_check=self.check, _quantity=4)

        category2 = make_recipe('category')

        data={
            'reference': 'just-trying...', # reference should never change
            'category': category2.code,
            'your_problem_notes': 'lorem2',
            'property_set': [],
            'dependants_young': 1,
            'dependants_old': 2,
        }
        response = self.client.put(
            self.detail_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEligibilityCheckResponseKeys(response)

        # checking the changed properties
        self.check.category = category2
        self.check.your_problem_notes = data['your_problem_notes']
        self.check.dependants_young = data['dependants_young']
        self.check.dependants_old = data['dependants_old']
        self.assertEligibilityCheckEqual(response.data, self.check)


    # Just check that eligibility check endpoint responds
    # in a sensible way

    def test_eligibility_check_not_exists_is_eligible_fail(self):
        wrong_ref = uuid.uuid4()
        response = self.client.post(self.get_is_eligible_url(wrong_ref), data={}, format='json',
                                    HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('core.viewsets.EligibilityChecker')
    def test_eligibility_check_is_eligible_pass(self, mocked_eligibility_checker):
        v = mocked_eligibility_checker()
        v.is_eligible.return_value = True
        response = self.client.post(
            self.get_is_eligible_url(self.check.reference),
            data={},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
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
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
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
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_eligible'], 'unknown')
