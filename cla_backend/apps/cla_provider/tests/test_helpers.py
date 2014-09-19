import mock
from collections import defaultdict

from django.test import TestCase

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
