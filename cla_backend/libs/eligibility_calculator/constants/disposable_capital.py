from ..util import BetweenDict


MORTGAGE_DISREGARD = 10000000
EQUITY_DISREGARD = 10000000

LIMIT_IMMIGRATION = 300000
LIMIT_DEFAULT = 800000


def get_limit(category):
    # TODO category:
    #   * final codes
    #   * no 800000 by default, return None in case of invalid codes
    if category == 'immigration':
        return LIMIT_IMMIGRATION

    return LIMIT_DEFAULT


PENSIONER_DISREGARD_LIMIT_LEVELS = BetweenDict({
    (0, 2600): 10000000,
    (2600, 5100): 9000000,
    (5100, 7600): 8000000,
    (7600, 10100): 7000000,
    (10100, 12600): 6000000,
    (12600, 15100): 5000000,
    (15100, 17600): 4000000,
    (17600, 20100): 3000000,
    (20100, 22600): 2000000,
    (22600, 31600): 1000000
})
