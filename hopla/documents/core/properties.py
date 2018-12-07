from abc import ABC, abstractmethod
from collections.abc import MutableMapping

import attr
from attr import NOTHING


NOTHING_DICT = dict(__value__=NOTHING)


@attr.s
class Properties(MutableMapping, ABC):
    data = attr.ib(default=dict(), type=dict)

    @data.validator
    def validate_data(self, _, __):
        # Initializing data
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, value):
        self.data.__delitem__(value)

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()

    @staticmethod
    @abstractmethod
    def from_dict(value):
        raise NotImplementedError
