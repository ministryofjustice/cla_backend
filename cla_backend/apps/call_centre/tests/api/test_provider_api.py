from datetime import timedelta
from itertools import cycle
from cla_provider.models import ProviderAllocation
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
        self.assertItemsEqual([d['name'] for d in response.data], [x.name for x in self.providers])

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
        self.operator.is_manager = True
        self.operator.save()
        self.categories = make_recipe('legalaid.category', _quantity=3)
        self.providers = make_recipe('cla_provider.provider',
                                     active=True,
                                     law_category=list(self.categories), _quantity=3)
        self.rotas = []

        category_generator = cycle(list(self.categories))
        start_date = timezone.now()
        for provider in self.providers:
            end_date = start_date + timedelta(days=7)
            self.rotas.append(
                make_recipe('cla_provider.outofhoursrota',
                            provider=provider,
                            start_date=start_date,
                            end_date=end_date,
                            category=next(category_generator)))
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
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertOutOfHoursRotaCheckResponseKeys(response2)

        self.assertOutOfHoursRotaEqual(post_data, response2)

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

        self.assertEqual(response.data['start_date'], self.rotas[0].start_date)

        # PATCH start date
        new_start_date = self.rotas[0].start_date + timedelta(days=1)
        response2 = self.client.patch(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json',
                                   data={
                                       'start_date': str(new_start_date)
                                   })

        self.assertOutOfHoursRotaCheckResponseKeys(response2)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertEqual(response2.data['start_date'], new_start_date)

    def test_delete_allowed(self):
        # CHECK ITEM EXISTS
        response = self.client.get(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertOutOfHoursRotaCheckResponseKeys(response)


        # DELETE IT
        response = self.client.delete(self.detail_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # CHECK LIST LEN =- 1


        response = self.client.get(self.list_url,
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.rotas)-1)

    def test_post_bad_category_not_allowed(self):
        """
        don't allow setting the category to one that
        the underlying provider isn't able to provide.
        """

        post_data = self._get_default_post_data()
        first_category = self.providers[0].law_category.all().first()
        ProviderAllocation.objects.filter(provider=self.providers[0],
                                          category=first_category).delete()


        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)
        self.assertEqual(response2.data,
                         {'__all__':
                              [u"Provider Name2 doesn't offer help for Name1"]})
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_overlapping_timespan_not_allowed_overlaps_exactly(self):
        """
        don't allow posting new rota entries that overlap other
            -   operator_id
            -   law category
            -   time span

        """
        post_data = self._get_default_post_data()


        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertOutOfHoursRotaCheckResponseKeys(response2)

        self.assertOutOfHoursRotaEqual(post_data, response2)

        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data,
                         {'__all__':
                              [u"Overlapping rota allocation not allowed"]})


    def test_post_overlapping_timespan_not_allowed_overlaps_end(self):
        """
        don't allow posting new rota entries that overlap other
            -   operator_id
            -   law category
            -   time span

        """
        post_data = self._get_default_post_data()


        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertOutOfHoursRotaCheckResponseKeys(response2)

        self.assertOutOfHoursRotaEqual(post_data, response2)

        post_data.update({
            'start_date': '2014-01-06T00:00:00Z',
            'end_date': '2014-01-08T00:00:00Z',
            })

        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data,
                         {'__all__':
                              [u"Overlapping rota allocation not allowed"]})

    def test_post_overlapping_timespan_not_allowed_overlaps_start(self):
        """
        don't allow posting new rota entries that overlap other
            -   operator_id
            -   law category
            -   time span

        """
        post_data = self._get_default_post_data()

        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertOutOfHoursRotaCheckResponseKeys(response2)

        self.assertOutOfHoursRotaEqual(post_data, response2)

        post_data.update({
            'start_date': '2013-12-30T00:00:00Z',
            'end_date': '2014-01-02T00:00:00Z',
            })

        response2 = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data,
                         {'__all__':
                              [u"Overlapping rota allocation not allowed"]})

    def test_end_date_must_be_greater_than_start_date(self):

        post_data = self._get_default_post_data()
        post_data.update({
            'start_date': '2014-01-07T00:00:00Z',
            'end_date': '2014-01-01T00:00:00Z',
        })
        response = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,
                         {'__all__': [u'End date must be after start date.']})

        # can't set same
        post_data = self._get_default_post_data()
        post_data.update({
            'start_date': '2014-01-07T00:00:00Z',
            'end_date': '2014-01-07T00:00:00Z',
        })
        response = self.client.post(self.list_url,
                                     HTTP_AUTHORIZATION='Bearer %s' % self.token,
                                     format='json',
                                     data=post_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,
                         {'__all__': [u'End date must be after start date.']})

    def test_non_manager_not_authorized(self):
        self.operator.is_manager = False
        self.operator.save()

        self._test_get_not_authorized(self.detail_url, self.token)
        self._test_get_not_authorized(self.list_url, self.token)
        self._test_post_not_authorized(self.list_url, self.token, self._get_default_post_data())
        self._test_patch_not_authorized(self.detail_url, self.token, self._get_default_post_data())
        self._test_delete_not_authorized(self.detail_url, self.token)