from collections import Mapping


class BetweenDict(Mapping):
    def __init__(self, d):
        """
        :param d: dict to use as basis for transform dict.
        It should have the form
        BetweenDict({
            (0, 10): 5,
            (10, 15): 25
        })

        where:
            (0, 10) == (<lower value included>, <upper value excluded>)


        NOTE:
            1. You cannot iterate over the between dict
            2. You cannot delete elements in the between dict
            2. len(betweenDict) will return the number of keys not expanded
        """
        self.store = dict()

        for k, v in d.items():
            if k[0] >= k[1]:
                raise ValueError(u"Invalid range (%s, %s)" % k[0], k[1])

            for lower, upper in self.store.keys():
                if not (k[1] <= lower or k[0] >= upper):
                    raise ValueError(u"Overlapping key spaces")
            self.store[k] = v

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __contains__(self, key):
        try:
            return bool(self.store[self.__keytransform__(key)]) or True
        except KeyError:
            return False

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        given_key = None
        for k, v in self.store.items():
            if k[0] <= key < k[1]:
                given_key = k
                break

        if not given_key:
            raise KeyError(key)
        return given_key
