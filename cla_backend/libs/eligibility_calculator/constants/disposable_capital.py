from ..util import BetweenDict


MORTGAGE_DISREGARD = 10000000
SMOD_DISREGARD = 10000000
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
    (0, 2500): 10000000,
    (2501, 5000): 9000000,
    (5001, 7500): 8000000,
    (7501, 10000): 7000000,
    (10001, 12500): 6000000,
    (12501, 15000): 5000000,
    (15001, 17500): 4000000,
    (17501, 20000): 3000000,
    (20001, 22500): 2000000,
    (22501, 31500): 1000000
})
