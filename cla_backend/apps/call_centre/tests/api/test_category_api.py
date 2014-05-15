from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe


class CategoryTests(CLAOperatorAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(CategoryTests, self).setUp()

        self.categories = make_recipe('legalaid.category', _quantity=3)

        self.list_url = reverse('call_centre:category-list')
        self.detail_url = reverse(
            'call_centre:category-detail', args=(),
            kwargs={'code': self.categories[0].code}
        )

    def test_get_allowed(self):
        """
        Ensure we can GET the list and it is ordered
        """
        # LIST
        response = self.client.get(self.list_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([d['name'] for d in response.data], ['Name1', 'Name2', 'Name3'])

        # DETAIL
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
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
