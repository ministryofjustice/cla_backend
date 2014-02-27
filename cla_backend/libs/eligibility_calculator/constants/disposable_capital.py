# TODO define BetweenDict
from ..util import BetweenDict


MORTGAGE_DISREGARD = 100000
EQUITY_DISREGARD = 100000


def get_limit(category):
	# TODO category
	if category == 'immigration':
		return 3000

	return 8000


PENSIONER_DISREGARD_LIMIT_LEVELS = BetweenDict({
    (0, 26): 100000,
    (26, 51): 90000,
    (51, 76): 80000,
    (76, 101): 70000,
    (101, 126): 60000,
    (126, 151): 50000,
    (151, 176): 40000,
    (176, 201): 30000,
    (201, 226): 20000,
    (226, 316): 10000
})
