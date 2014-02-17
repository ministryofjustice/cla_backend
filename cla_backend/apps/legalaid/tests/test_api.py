import uuid
from model_mommy.recipe import Recipe, seq, foreign_key

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase

from ..models import Category, EligibilityCheck, Property, Finance

from .test_base import CLABaseApiTestMixin


category_recipe = Recipe(Category,
    name=seq('Name'), order = seq(0)
)

finance_recipe = Recipe(Finance)

eligibility_check_recipe = Recipe(EligibilityCheck,
    dependants_young=5, dependants_old=6,
    your_finances=foreign_key(finance_recipe),
    partner_finances=foreign_key(finance_recipe)
)

property_recipe = Recipe(Property,
    eligibility_check=foreign_key(eligibility_check_recipe)
)



class CategoryTests(CLABaseApiTestMixin, APITestCase):
    def setUp(self):
        super(CategoryTests, self).setUp()

        self.categories = category_recipe.make(_quantity=3)

        self.list_url = reverse('category-list')
        self.detail_url = reverse('category-detail', args=(), kwargs={'pk': 1})

    def test_get_allowed(self):
        """
        Ensure we can GET the list and it is ordered
        """

        # LIST
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([d['name'] for d in response.data], ['Name1', 'Name2', 'Name3'])

        # DETAIL
        response = self.client.get(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Name1')

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """

        ### LIST
        self._test_post_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        ### DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)


class EligibilityCheckTests(CLABaseApiTestMixin, APITestCase):
    def setUp(self):
        super(EligibilityCheckTests, self).setUp()

        self.list_url = reverse('eligibility_check-list')
        self.check = eligibility_check_recipe.make(
            category=category_recipe.make(),
            notes=u'lorem ipsum'
        )
        self.detail_url = reverse(
            'eligibility_check-detail', args=(),
            kwargs={'reference': str(self.check.reference)}
        )

    def assertResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['reference', 'category', 'notes',
             'property_set', 'dependants_young',
             'dependants_old', 'your_finances',
             'partner_finances']
        )

    def assertFinanceEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['bank_balance', 'investment_balance', 'asset_balance', 'credit_balance', 'earnings', 'other_income', 'self_employed']:
                self.assertEqual(getattr(obj, prop), data[prop])

    def assertEligibilityCheckEqual(self, data, check):
        self.assertEqual(data['reference'], str(check.reference))
        self.assertEqual(data['category'], check.category.id if check.category else None)
        self.assertEqual(data['notes'], check.notes)
        self.assertEqual(len(data['property_set']), check.property_set.count())
        self.assertEqual(data['dependants_young'], check.dependants_young)
        self.assertEqual(data['dependants_old'], check.dependants_old)
        self.assertFinanceEqual(data['your_finances'], check.your_finances)
        self.assertFinanceEqual(data['partner_finances'], check.partner_finances)

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
            self.list_url, data={}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
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
        category_recipe.make()

        category = Category.objects.all()[0]
        data={
            'category': category.pk,
            'notes': 'lorem',
            'dependants_young': 2,
            'dependants_old': 3,
        }
        response = self.client.post(
            self.list_url, data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEligibilityCheckEqual(response.data,
            EligibilityCheck(
                reference=response.data['reference'],
                category=category, notes=data['notes'],
                dependants_young=2, dependants_old=3
            )
        )

    def test_create_with_properties(self):
        """
        CREATE data with properties
        """
        data={
            'property_set': [
                {'value': 111, 'equity': 222, 'share': 33},
                {'value': 999, 'equity': 888, 'share': 77}
            ]
        }
        response = self.client.post(
            self.list_url, data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEqual(response.data['category'], None)
        self.assertEqual(response.data['notes'], '')
        self.assertEqual(len(response.data['property_set']), 2)
        self.assertEqual(response.data['dependants_young'], 0)
        self.assertEqual(response.data['dependants_old'], 0)
        self.assertItemsEqual([p['id'] for p in response.data['property_set']], [1,2])
        self.assertItemsEqual([p['value'] for p in response.data['property_set']], [111, 999])
        self.assertItemsEqual([p['equity'] for p in response.data['property_set']], [222, 888])
        self.assertItemsEqual([p['share'] for p in response.data['property_set']], [33, 77])

    def test_create_with_finances(self):
        """
        CREATE data with finances
        """
        data={
            'your_finances': {
                "bank_balance": 100,
                "investment_balance": 200,
                "asset_balance": 300,
                "credit_balance": 400,
                "earnings": 500,
                "other_income": 600,
                "self_employed": True
            },
            'partner_finances': {
                "bank_balance": 1000,
                "investment_balance": 2000,
                "asset_balance": 3000,
                "credit_balance": 4000,
                "earnings": 5000,
                "other_income": 6000,
                "self_employed": False
            },
        }
        response = self.client.post(
            self.list_url, data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertResponseKeys(response)
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEqual(response.data['category'], None)
        self.assertEqual(response.data['notes'], '')
        self.assertEqual(len(response.data['property_set']), 0)
        self.assertEqual(response.data['dependants_young'], 0)
        self.assertEqual(response.data['dependants_old'], 0)
        self.assertDictEqual(response.data['your_finances'], data['your_finances'])
        self.assertDictEqual(response.data['partner_finances'], data['partner_finances'])

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        data={
            'category': -1,
            'notes': 'a'*501,
            'property_set': [
                {'value': 111, 'equity': 222, 'share': 33},  # valid
                {'value': -1, 'equity': -1, 'share': -1},  # invalid
                {'value': 0, 'equity': 0, 'share': 101},  # invalid
            ],
            'dependants_young': -1,
            'dependants_old': -1,
            'your_finances': {
                "bank_balance": -1,
                "investment_balance": -1,
                "asset_balance": -1,
                "credit_balance": -1,
                "earnings": -1,
                "other_income": -1
            },
            'partner_finances': {
                "bank_balance": -1,
                "investment_balance": -1,
                "asset_balance": -1,
                "credit_balance": -1,
                "earnings": -1,
                "other_income": -1
            },
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data
        self.assertItemsEqual(
            errors.keys(),
            [
                'category', 'notes', 'property_set', 'dependants_young',
                'dependants_old', 'your_finances', 'partner_finances'
            ]
        )
        self.assertEqual(errors['category'], [u"Invalid pk '-1' - object does not exist."])
        self.assertEqual(errors['notes'], [u'Ensure this value has at most 500 characters (it has 501).'])
        self.assertItemsEqual(errors['property_set'], [
            {},
            {
                'share': [u'Ensure this value is greater than or equal to 0.'],
                'value': [u'Ensure this value is greater than or equal to 0.'],
                'equity': [u'Ensure this value is greater than or equal to 0.']
            },
            {'share': [u'Ensure this value is less than or equal to 100.']}
        ])
        self.assertEqual(errors['dependants_young'], [u'Ensure this value is greater than or equal to 0.'])
        self.assertEqual(errors['dependants_old'], [u'Ensure this value is greater than or equal to 0.'])
        self.assertItemsEqual(
            errors['your_finances'],
            [
                {
                    'credit_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'asset_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'investment_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'earnings': [u'Ensure this value is greater than or equal to 0.'],
                    'bank_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'other_income': [u'Ensure this value is greater than or equal to 0.']
                }
            ]
        )
        self.assertItemsEqual(
            errors['partner_finances'],
            [
                {
                    'credit_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'asset_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'investment_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'earnings': [u'Ensure this value is greater than or equal to 0.'],
                    'bank_balance': [u'Ensure this value is greater than or equal to 0.'],
                    'other_income': [u'Ensure this value is greater than or equal to 0.']
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
            'eligibility_check-detail', args=(),
            kwargs={'reference': uuid.uuid4()}
        )

        response = self.client.get(not_found_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_object(self):
        """
        GET should not return properties of other eligibility check objects
        """
        property_recipe.make(eligibility_check=self.check, _quantity=4)

        # making extra properties
        property_recipe.make(_quantity=5)

        self.assertEqual(Property.objects.count(), 9)

        response = self.client.get(self.detail_url, format='json')
        self.assertResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)

    # PATCH

    def test_patch_no_data(self):
        """
        PATCH data is empty so the object shouldn't change
        """
        response = self.client.patch(
            self.detail_url, data={}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertResponseKeys(response)
        self.assertEligibilityCheckEqual(response.data, self.check)

    def test_patch_basic_data(self):
        """
        PATCH data is not empty so the object should change
        """
        category2 = category_recipe.make()

        data={
            'reference': 'just-trying...', # reference should never change
            'category': category2.pk,
            'notes': 'lorem ipsum2',
            'dependants_young': 10,
            'dependants_old': 10,
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['reference'], str(self.check.reference))
        self.assertEqual(response.data['category'], data['category'])
        self.assertEqual(response.data['notes'], data['notes'])
        self.assertEqual(response.data['property_set'], [])
        self.assertEqual(response.data['dependants_young'], data['dependants_young'])
        self.assertEqual(response.data['dependants_old'], data['dependants_old'])
        self.assertFinanceEqual(response.data['your_finances'], Finance())
        self.assertFinanceEqual(response.data['partner_finances'], Finance())

    def test_patch_properties(self):
        """
        PATCH should add/remove/change properties.
        """
        property_recipe.make(eligibility_check=self.check, _quantity=4)

        # making extra properties
        property_recipe.make(_quantity=5)

        self.assertItemsEqual(self.check.property_set.values_list('id', flat=True), [1,2,3,4])

        # changing property with id == 1, removing all the others and adding
        # an extra one
        data={
            'property_set': [
                {'value': 111, 'equity': 222, 'share': 33, 'id': 1},
                {'value': 999, 'equity': 888, 'share': 77}
            ]
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # nothing should have changed here
        self.assertEqual(response.data['reference'], str(self.check.reference))
        self.assertEqual(response.data['category'], self.check.category.id)
        self.assertEqual(response.data['notes'], self.check.notes)
        self.assertEqual(response.data['dependants_young'], self.check.dependants_young)
        self.assertEqual(response.data['dependants_old'], self.check.dependants_old)

        # properties should have changed. The new property should have id == 10
        self.assertEqual(len(response.data['property_set']), 2)
        self.assertItemsEqual([p['id'] for p in response.data['property_set']], [1,10])
        self.assertItemsEqual([p['value'] for p in response.data['property_set']], [111, 999])
        self.assertItemsEqual([p['equity'] for p in response.data['property_set']], [222, 888])
        self.assertItemsEqual([p['share'] for p in response.data['property_set']], [33, 77])

        # checking the db just in case
        self.assertItemsEqual(self.check.property_set.values_list('id', flat=True), [1,10])

    def test_patch_with_finances(self):
        """
        PATCH should change finances.
        """
        data={
            'your_finances': {
                "bank_balance": 100,
                "investment_balance": 200,
                "asset_balance": 300,
                "credit_balance": 400,
                "earnings": 500,
                "other_income": 600,
                "self_employed": True
            },
            'partner_finances': {
                "bank_balance": 1000,
                "investment_balance": 2000,
                "asset_balance": 3000,
                "credit_balance": 4000,
                "earnings": 5000,
                "other_income": 6000,
                "self_employed": False
            },
        }
        response = self.client.patch(
            self.detail_url, data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['reference'], str(self.check.reference))
        self.assertEqual(response.data['category'], self.check.category.id)
        self.assertEqual(response.data['notes'], self.check.notes)
        self.assertEqual(response.data['dependants_young'], self.check.dependants_young)
        self.assertEqual(response.data['dependants_old'], self.check.dependants_old)

        self.assertDictEqual(response.data['your_finances'], data['your_finances'])
        self.assertDictEqual(response.data['partner_finances'], data['partner_finances'])

    def test_patch_in_error(self):
        self._test_method_in_error('patch', self.detail_url)

    def test_others_property_cannot_be_set(self):
        """
        other_property is assigned to another eligibility_check.

        We try to assign this other_property to our self.check.

        The endpoint should NOT change the other_property and our self.check.property_set
        should NOT point to other_property.
        """
        other_property = property_recipe.make(id=1)
        data={
            'property_set': [
                {'value': 0, 'equity': 0, 'share': 0, 'id': other_property.pk}
            ]
        }
        response = self.client.patch(
            self.detail_url, data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['property_set'][0]['id'], 2)
        self.assertNotEqual(other_property.eligibility_check.pk, self.check.pk)

    # PUT

    def test_put_basic_data(self):
        """
        PUT should override the values
        """
        property_recipe.make(eligibility_check=self.check, _quantity=4)

        category2 = category_recipe.make()

        data={
            'reference': 'just-trying...', # reference should never change
            'category': category2.pk,
            'notes': 'lorem2',
            'property_set': [],
            'dependants_young': 1,
            'dependants_old': 2,
        }
        response = self.client.put(
            self.detail_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertResponseKeys(response)
        self.assertEqual(response.data['reference'], str(self.check.reference))
        self.assertEqual(response.data['category'], data['category'])
        self.assertEqual(response.data['notes'], 'lorem2')
        self.assertEqual(response.data['property_set'], [])
        self.assertEqual(response.data['dependants_young'], data['dependants_young'])
        self.assertEqual(response.data['dependants_old'], data['dependants_old'])
        self.assertFinanceEqual(response.data['your_finances'], Finance())
        self.assertFinanceEqual(response.data['partner_finances'], Finance())


class EligibilityCheckPropertyTests(CLABaseApiTestMixin, APITestCase):
    def setUp(self):
        super(EligibilityCheckPropertyTests, self).setUp()

        self.check = property_recipe.make(
            value=100000,
            equity=20000,
            share=50,
        )
        parent_ref = str(self.check.eligibility_check.reference)
        self.list_url = reverse('property-list',
                                args=[parent_ref])

        self.detail_url = reverse(
            'property-detail', args=[parent_ref, self.check.id]
        )


    def test_create_no_data(self):
        """
        CREATE data is empty
        """
        response = self.client.post(self.list_url, data={}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertItemsEqual(response.data.keys(), ['value', 'equity', 'share', 'id'])
        self.assertTrue(response.data['id'] > self.check.id)
        self.assertEqual(response.data['value'], 0)
        self.assertEqual(response.data['equity'], 0)
        self.assertEqual(response.data['share'], 0)

    def test_post_full_data(self):
        response = self.client.post(self.list_url,
                                    data=
                                    {
                                        'value': self.check.value,
                                        'equity': self.check.equity,
                                        'share': self.check.share
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['id'] > self.check.id)
        self.assertEqual(response.data['value'], self.check.value)
        self.assertEqual(response.data['equity'], self.check.equity)
        self.assertEqual(response.data['share'], self.check.share)


    def test_patch_full_data(self):
        response = self.client.patch(self.detail_url,
                                     data=
                                     {
                                         'value': self.check.value-1,
                                         'share': self.check.share-1,
                                         'equity': self.check.equity-1
                                     })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['id'] == self.check.id)
        self.assertTrue(response.data['value'] == self.check.value-1)
        self.assertTrue(response.data['share'] == self.check.share-1)
        self.assertTrue(response.data['equity'] == self.check.equity-1)

        # make sure it actually saved
        response2 = self.client.get(self.detail_url)
        self.assertEqual(response.data, response2.data)



    def test_put_full_data(self):
        response = self.client.put(self.detail_url,
                                     data=
                                     {
                                         'value': self.check.value-1,
                                         'share': self.check.share-1,
                                         'equity': self.check.equity-1
                                     })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['id'] == self.check.id)
        self.assertTrue(response.data['value'] == self.check.value-1)
        self.assertTrue(response.data['share'] == self.check.share-1)
        self.assertTrue(response.data['equity'] == self.check.equity-1)

        # make sure it actually saved
        response2 = self.client.get(self.detail_url)
        self.assertEqual(response.data, response2.data)


    def test_put_partial_data(self):
        response = self.client.put(self.detail_url,
                                   data=
                                   {
                                       'value': self.check.value-1,
                                   })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['id'] == self.check.id)
        self.assertTrue(response.data['value'] == self.check.value-1)

        # was not sent by us so should be default
        self.assertTrue(response.data['share'] == 0)
        self.assertTrue(response.data['equity'] == 0)

        # make sure it actually saved
        response2 = self.client.get(self.detail_url)
        self.assertEqual(response.data, response2.data)

    def test_delete_object(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)

        response2 = self.client.get(self.detail_url)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)


