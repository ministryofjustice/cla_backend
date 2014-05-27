from random import random
from operator import itemgetter

from cla_provider.models import ProviderAllocation


class ProviderAllocationHelper(object):

    def __init__(self):
        self._providers_in_category = None

    def get_qualifying_providers_allocation(self, category):
        """
        @return: list
        """
        if not self._providers_in_category:
            self._providers_in_category = ProviderAllocation.objects.filter(category=category)

        return self._providers_in_category


    def get_qualifying_providers(self, category):
        """
        @return: list
        """
        return [pa.provider for pa in self.get_qualifying_providers_allocation(category)]

    def get_random_provider(self, category):
        """
        @return: Randomly chosen provider who offers this category of service
                 or None if there are no providers with this category of service
        """
        # the score_card is only built to make inspecting this procedure easier.
        # The alternative is to only store a single winner which is updated on
        # each iteration
        score_card = [] # of (provider.id => weighted_score)
        for pa in self.get_qualifying_providers_allocation(category):
            # calculate score for each provider
            score_card.append((pa.provider.id, float(pa.weighted_distribution) * random()))
        if not score_card:
            return None

        # the highest score wins
        winner = sorted(score_card, key=itemgetter(1), reverse=True)[0]
        return winner[0]
