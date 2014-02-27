# TODO define BetweenDict
from something import BetweenDict


MORTGAGE_DISREGARD = 100000
EQUITY_DISREGARD = 100000


def get_limit(category):
	# TODO category
	if category == 'immigration':
		return 3000

	return 8000


PENSIONER_DISREGARD_LIMIT_LEVELS = BetweenDict({
	0: 100000,
	26: 90000,
	51: 80000,
	76: 70000,
	101: 60000,
	126: 50000,
	151: 40000,
	176: 30000,
	201: 20000,
	226: 10000,
	316: 0
})
