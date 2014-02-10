from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class CategoryTests(APITestCase):
    def test_methods_allowed(self):
        """
        Ensure we can create a new account object.
        """
        # GET allowed
        url = reverse('legalaid:category-list')
        response = self.client.get(url, data, format='json')
        # import pdb; pdb.set_trace()

        # data = {'name': 'DabApps'}
        # response = self.client.post(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data, data)
