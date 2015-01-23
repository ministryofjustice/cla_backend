from cla_provider.models import ProviderAllocation
import mock
import datetime
from collections import defaultdict

from django.test import TestCase
from django.utils import timezone

from core.tests.mommy_utils import make_recipe

from cla_provider.helpers import ProviderAllocationHelper


class ProviderAllocationHelperTestCase(TestCase):
    def build_providers(self, providers_data):
        providers = []
        for id, pa in providers_data.items():
            providers.append(
                mock.MagicMock(
                    provider=mock.MagicMock(id=id),
                    weighted_distribution=pa['weight']
                )
            )
        return providers

    def _test__get_random_provider(self, alloc_data, num_iterations=100000):
        # print "\n\nNew test"
        helper = ProviderAllocationHelper()
        helper._providers_in_category = self.build_providers(alloc_data)

        results = defaultdict(int)
        category = mock.MagicMock()
        for i in range(0, num_iterations):
            winner = helper._get_random_provider(category)
            results[winner.id] += 1

        for id, count in results.items():
            prob = (count * 100.) / num_iterations
            # print 'expected %s - found %s. Difference %s' % (
            #     alloc_data[id]['expected_prob'], prob,
            #     ((alloc_data[id]['expected_prob'] * 0.01) * num_iterations) - \
            #     ((prob * 0.01) * num_iterations)
            # )
            self.assertAlmostEqual(prob, alloc_data[id]['expected_prob'], delta=1.5)

    def test__get_random_provider(self):
        # weight as integers
        self._test__get_random_provider({
            20: {'weight': 20, 'expected_prob': 20},
            30: {'weight': 30, 'expected_prob': 30},
            50: {'weight': 50, 'expected_prob': 50},
        })

        # weight as floats
        self._test__get_random_provider({
            28: {'weight': 2.8, 'expected_prob': 28},
            27: {'weight': 2.7, 'expected_prob': 27},
            4: {'weight': 0.4, 'expected_prob': 4},
            5: {'weight': 0.5, 'expected_prob': 5},
            13: {'weight': 1.3, 'expected_prob': 13},
            1: {'weight': 0.1, 'expected_prob': 1},
            10: {'weight': 1., 'expected_prob': 10},
            12: {'weight': 1.2, 'expected_prob': 12},
        })

        # 2 items
        self._test__get_random_provider({
            1: {'weight': 1, 'expected_prob': 1},
            99: {'weight': 99, 'expected_prob': 99},
        })

        # # same weight
        self._test__get_random_provider({
            1: {'weight': 0.8, 'expected_prob': 33.3},
            2: {'weight': 0.8, 'expected_prob': 33.3},
            3: {'weight': 0.8, 'expected_prob': 33.3},
        })

        # 0 weight
        self._test__get_random_provider({
            0: {'weight': 0, 'expected_prob': 0},
            100: {'weight': 2, 'expected_prob': 100},
        })

    @mock.patch('cla_provider.helpers.ProviderAllocation')
    def test__get_random_provider_with_empty_list(self, MockedProviderAllocation):
        MockedProviderAllocation.objects.filter.return_value = []

        helper = ProviderAllocationHelper()

        winner = helper._get_random_provider(mock.MagicMock())
        self.assertEqual(winner, None)

    def test_get_qualifying_providers(self):
        category1 = make_recipe('legalaid.category')
        category2 = make_recipe('legalaid.category')

        cat1_provider1 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=cat1_provider1,
            category=category1
        )

        cat1_provider2 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=cat1_provider2,
            category=category1
        )

        cat2_provider1 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=cat2_provider1,
            category=category2
        )

        helper = ProviderAllocationHelper()
        cat1_providers = helper.get_qualifying_providers(category1)
        self.assertItemsEqual(
            cat1_providers, [cat1_provider1, cat1_provider2]
        )

        # Set cat1_provider2.active == False => only one prov returned
        cat1_provider2.active = False
        cat1_provider2.save()

        helper = ProviderAllocationHelper()
        cat1_providers = helper.get_qualifying_providers(category1)
        self.assertItemsEqual(
            cat1_providers, [cat1_provider1]
        )

    def test_get_suggested_provider_random(self):

        as_of = timezone.make_aware(
            datetime.datetime(day=8, month=12, year=2014, hour=10, minute=0),
            timezone.get_current_timezone()
        )

        category = make_recipe('legalaid.category')

        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=provider,
            category=category
        )

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper._get_random_provider(category)
        self.assertEqual(choosen_provider, provider)

        # Set cat1_provider2.active == False => only one prov returned
        provider.active = False
        provider.save()

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, None)


    def test_get_suggested_provider_best_fit(self):
        # slightly brute force test

        as_of = timezone.make_aware(
            datetime.datetime(day=8, month=12, year=2014, hour=10, minute=0),
            timezone.get_current_timezone()
        )

        category = make_recipe('legalaid.category')

        provider1 = make_recipe('cla_provider.provider', active=True)
        provider2 = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=0.5,
            provider=provider1,
            category=category,
        )
        make_recipe(
            'cla_provider.provider_allocation',
            weighted_distribution=1,
            provider=provider2,
            category=category,
        )
        ProviderAllocation.objects.update(modified=as_of-datetime.timedelta(days=1))

        helper = ProviderAllocationHelper(as_of=as_of)
        counts = {provider1: 0, provider2: 0}
        # quick sanity check that random allocation is working
        for i in range(100):
            sugg = helper.get_suggested_provider(category)
            counts[sugg] = counts[sugg] + 1
        self.assertTrue(counts[provider2] > counts[provider1])

        case1 = make_recipe('legalaid.eligible_case', diagnosis__category=category)
        case1.assign_to_provider(provider1)


        # cases assigned at != today are ignored, so expect same as before
        counts = {provider1: 0, provider2: 0}
        for i in range(100):
            sugg = helper.get_suggested_provider(category)
            counts[sugg] = counts[sugg] + 1
        self.assertTrue(counts[provider2] > counts[provider1])


        case1.provider_assigned_at = as_of
        case1.save()

        for i in range(100):
            self.assertEqual(helper.get_suggested_provider(category), provider2)
            # should always be provider 2


    def test_get_suggested_provider_rota(self):
        as_of = timezone.make_aware(
            datetime.datetime(day=7, month=12, year=2014, hour=10, minute=0),
            timezone.get_current_timezone()
        )

        category = make_recipe('legalaid.category')

        provider = make_recipe('cla_provider.provider', active=True)
        make_recipe(
            'cla_provider.outofhoursrota',
            provider=provider,
            start_date=as_of,
            end_date=as_of + datetime.timedelta(days=1),
            category=category
        )

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, provider)

        # Set cat1_provider2.active == False => only one prov returned
        provider.active = False
        provider.save()

        helper = ProviderAllocationHelper(as_of=as_of)
        choosen_provider = helper.get_suggested_provider(category)
        self.assertEqual(choosen_provider, None)
