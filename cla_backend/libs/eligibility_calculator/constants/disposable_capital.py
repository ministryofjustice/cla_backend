# TODO define BetweenDict
from ..util import BetweenDict


MORTGAGE_DISREGARD = 10000000
EQUITY_DISREGARD = 10000000


def get_limit(category):
	# TODO category
	if category == 'immigration':
		return 300000

	return 800000


PENSIONER_DISREGARD_LIMIT_LEVELS = BetweenDict({
    (0, 26): 10000000,
    (26, 51): 9000000,
    (51, 76): 8000000,
    (76, 101): 7000000,
    (101, 126): 6000000,
    (126, 151): 5000000,
    (151, 176): 4000000,
    (176, 201): 3000000,
    (201, 226): 2000000,
    (226, 316): 1000000
})
