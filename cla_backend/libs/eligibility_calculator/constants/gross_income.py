BASE_LIMIT = 2657

INCLUSIVE_CHILDREN_BASE = 4

EXTRA_CHILD_MODIFIER = 222


def get_limit(dependant_children=0):
	limit = BASE_LIMIT
	limit += max(0, dependant_children-INCLUSIVE_CHILDREN_BASE) * EXTRA_CHILD_MODIFIER
	return limit
