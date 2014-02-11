from model_mommy.recipe import Recipe, seq

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Category

from .test_base import CLABaseApiTestMixin


category_recipe = Recipe(Category,
    name=seq('Name'), order = seq(0)
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
