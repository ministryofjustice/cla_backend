from datetime import timedelta
from itertools import cycle
from dateutil import parser
from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe


class ProviderTests(CLAOperatorAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(ProviderTests, self).setUp()

        self.providers = make_recipe('cla_provider.provider', active=True, _quantity=3)

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

class OutOfHoursRotaTests(CLAOperatorAuthBaseApiTestMixin, APITestCase):


    def assertOutOfHoursRotaCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            [
                'id',
                'start_date',
                'end_date',
                'category',
                'provider'
            ]
        )

    def setUp(self):
        super(OutOfHoursRotaTests, self).setUp()
        self.categories = make_recipe('legalaid.category', _quantity=3)
        self.providers = make_recipe('cla_provider.provider',
                                     active=True,
                                     law_category=self.categories, _quantity=3)
        self.rotas = []


        start_date = timezone.now()
        for provider in self.providers:
            end_date = start_date + timedelta(days=7)
            self.rotas.append(
                make_recipe('cla_provider.outofhoursrota',
                            provider=provider,
                            start_date=start_date,
                            end_date=end_date))
            start_date = end_date

        self.list_url = reverse('call_centre:outofhoursrota-list')
        self.provider_list_url = reverse('call_centre:provider-list')
        self.detail_url = reverse(
            'call_centre:outofhoursrota-detail', args=(),
            kwargs={'pk': self.rotas[0].pk}
        )


    def _get_default_post_data(self):
        return {
            'start_date': '2014-01-01T00:00:00Z',
            'end_date': '2014-01-07T00:00:00Z',
            'provider': self.providers[0].pk,
            'category': self.providers[0].law_category.all().first().code
        }

    def assertOutOfHoursRotaEqual(self, post_data, response_data):
        self.assertEqual(response_data.data['start_date'],
                         parser.parse(post_data['start_date']))
        self.assertEqual(response_data.data['end_date'],
                         parser.parse(post_data['end_date']))
        self.assertEqual(response_data.data['category'], post_data['category'])
        self.assertEqual(response_data.data['provider'], post_data['provider'])

    def test_get_allowed(self):
        """
        Test that we can get a rota list and an rota detail
        """

        # LIST
        response = self.client.get(self.list_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual(response.data,
            [{
                'id': rota.id,
                'start_date': rota.start_date,
                'end_date': rota.end_date,
                'category': rota.category.code,
                'provider': rota.provider_id
            } for rota in self.rotas])

        # DETAIL
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertOutOfHoursRotaCheckResponseKeys(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.rotas[0].id)



    def test_post_allowed(self):

        response1 = self.client.get(self.list_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        before_len = len(response1.data)


        post_data = self._get_default_post_data()
        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertOutOfHoursRotaCheckResponseKeys(response2)

        self.assertOutOfHoursRotaEqual(post_data, response2.data)

        response3 = self.client.get(self.list_url,
                                    HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                    format='json')

        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(before_len + 1, len(response3.data))

    def test_patch_allowed(self):
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertOutOfHoursRotaCheckResponseKeys(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.rotas[0].id)