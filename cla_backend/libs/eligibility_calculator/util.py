from collections import Mapping


class BetweenDict(Mapping):
    def __init__(self, d):
        """

        :param d: dict to use as basis for transform dict.
        It should have the form
        BetweenDict({
            (0,10): 5,
            (10, 15): 25
        })
        """
        self.store = dict()

        for k, v in d.items():
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
