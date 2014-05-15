from model_mommy import mommy

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin


def cla_provider_make_recipe(model_name, **kwargs):
    return mommy.make_recipe('cla_provider.tests.%s' % model_name, **kwargs)


class ProviderTests(CLAOperatorAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(ProviderTests, self).setUp()

        self.providers = mommy.make_recipe('cla_provider.tests.provider', active=True, _quantity=3)

        self.list_url = reverse('call_centre:provider-list')
        self.detail_url = reverse(
            'call_centre:provider-detail', args=(),
            kwargs={'pk': self.providers[0].pk}
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
        self.assertEqual([d['name'] for d in response.data], [x.name for x in self.providers])

        # DETAIL
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.providers[0].name)

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

    def test_provider_response_fields(self):

        response = self.client.get(self.detail_url,
                           HTTP_AUTHORIZATION='Bearer %s' % self.token,
                           format='json')
        self.assertItemsEqual(
            response.data.keys(),
            ['name',
             'id',
             'short_code',
             'telephone_frontdoor',
             'telephone_backdoor'
             ]
        )
