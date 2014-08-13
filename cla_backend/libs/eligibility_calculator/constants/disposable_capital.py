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
    (0, 2501): 10000000,
    (2501, 5001): 9000000,
    (5001, 7501): 8000000,
    (7501, 10001): 7000000,
    (10001, 12501): 6000000,
    (12501, 15001): 5000000,
    (15001, 17501): 4000000,
    (17501, 20001): 3000000,
    (20001, 22501): 2000000,
    (22501, 31501): 1000000
})
