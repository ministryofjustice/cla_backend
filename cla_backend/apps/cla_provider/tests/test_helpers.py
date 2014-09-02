import mock
from django.test import TestCase

from cla_provider.helpers import ProviderAllocationHelper


class ProviderAllocationHelperTestCase(TestCase):
    def build_providers(self, providers_data):
        providers = []
        for data in providers_data:
            providers.append(
                mock.MagicMock(
                    provider=mock.MagicMock(id=data['id']),
                    weighted_distribution=data['weighted_distribution']
                )
            )
        return providers

    def test__get_random_provider(self):
        helper = ProviderAllocationHelper()
        helper._providers_in_category = self.build_providers([
            {'id': 20, 'weighted_distribution': 20},
            {'id': 30, 'weighted_distribution': 30},
            {'id': 50, 'weighted_distribution': 50}
        ])


        results = {
            20: 0, 30: 0, 50: 0
        }
        num_iterations = 100000
        for i in range(0, num_iterations):
            winner = helper._get_random_provider(None)
            results[winner.id] += 1

        for id, choosen_count in results.items():
            print 'id %s: %s %%' % (id, (choosen_count * 100.) / num_iterations)
