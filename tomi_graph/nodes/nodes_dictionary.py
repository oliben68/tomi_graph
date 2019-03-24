from collections.abc import MutableMapping


class NodesDictionary(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._dict = {}
        self._immutable_keys = []

        self._dict.update(*args, **kwargs)

    def protect(self, key):
        self._immutable_keys.append(key)
        self._immutable_keys = list(set(self._immutable_keys))

    def lift_protection(self, key):
        self._immutable_keys.remove(key)

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        if key not in self._immutable_keys:
            del self._dict[key]

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __str__(self):
        return str(self._dict)

    def __repr__(self):
        return repr(self._dict)
