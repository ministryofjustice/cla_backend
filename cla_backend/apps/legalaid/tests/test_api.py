from model_mommy.recipe import Recipe, seq

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Category, EligibilityCheck

from .test_base import CLABaseApiTestMixin


category_recipe = Recipe(Category,
    name=seq('Name'), order = seq(0)
)

eligibility_check_recipe = Recipe(EligibilityCheck)


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


    def test_create_no_data(self):
        """
        CREATE data is empty
        """
        response = self.client.post(
            self.list_url, data={}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertItemsEqual(response.data.keys(), ['reference', 'category', 'notes'])
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEqual(response.data['category'], None)
        self.assertEqual(response.data['notes'], '')

    def test_create_full_data(self):
        """
        CREATE data is not empty
        """
        category_recipe.make()

        data={
            'category': Category.objects.all()[0].pk,
            'notes': 'lorem'
        }
        response = self.client.post(
            self.list_url, data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertItemsEqual(response.data.keys(), ['reference', 'category', 'notes'])
        self.assertTrue(len(response.data['reference']) > 30)
        self.assertEqual(response.data['category'], data['category'])
        self.assertEqual(response.data['notes'], data['notes'])

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_get_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        ### DETAIL
        self._test_get_not_allowed(self.detail_url)
        self._test_post_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)

    def test_patch_no_data(self):
        """
        PATCH data is empty so the object shouldn't change
        """
        response = self.client.patch(
            self.detail_url, data={}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertItemsEqual(response.data.keys(), ['reference', 'category', 'notes'])
        self.assertTrue(response.data['reference'] > self.check.reference)
        self.assertEqual(response.data['category'], self.check.category.pk)
        self.assertEqual(response.data['notes'], self.check.notes)

    def test_patch_full_data(self):
        """
        PATCH data is not empty so the object should change
        """
        category2 = category_recipe.make()

        data={
            'reference': 'just-trying...', # reference should never change
            'category': category2.pk,
            'notes': 'lorem ipsum2'
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertItemsEqual(response.data.keys(), ['reference', 'category', 'notes'])
        self.assertEqual(response.data['reference'], str(self.check.reference))
        self.assertEqual(response.data['category'], data['category'])
        self.assertEqual(response.data['notes'], data['notes'])

    def test_put_full_data(self):
        """
        PUT data is not empty so the object should change
        """
        category2 = category_recipe.make()

        data={
            'reference': 'just-trying...', # reference should never change
            'category': category2.pk,
            'notes': 'lorem ipsum2'
        }
        response = self.client.put(
            self.detail_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertItemsEqual(response.data.keys(), ['reference', 'category', 'notes'])
        self.assertEqual(response.data['reference'], str(self.check.reference))
        self.assertEqual(response.data['category'], data['category'])
        self.assertEqual(response.data['notes'], data['notes'])
