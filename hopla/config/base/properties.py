import random
import string
from collections.abc import MutableMapping


class Properties(MutableMapping):
    _INNER_ = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))

    @staticmethod
    def prep_value(value):
        return value if type(value) != dict and not issubclass(type(value), dict) else Properties(value)

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("{klass} expected at most 1 arguments, got {cnt}".format(klass=type(self).__name__,
                                                                                     cnt=len(args)))
        setattr(self, Properties._INNER_, dict())

        if len(args) == 1:
            getattr(self, Properties._INNER_).__init__(**{k: Properties.prep_value(v) for k, v in args[0].items()})

        if len(kwargs) > 0:
            getattr(self, Properties._INNER_).update({k: Properties.prep_value(v) for k, v in kwargs.items()})

    def __setitem__(self, key, value):
        getattr(self, Properties._INNER_)[key] = Properties.prep_value(value)

    def __delitem__(self, value):
        getattr(self, Properties._INNER_).__delitem__(value)

    def __getitem__(self, key):
        return getattr(self, Properties._INNER_)[key]

    def __len__(self):
        return len(getattr(self, Properties._INNER_))

    def __iter__(self):
        return getattr(self, Properties._INNER_).__iter__()

    def __str__(self):
        return str(getattr(self, Properties._INNER_))

    def __repr__(self):
        return repr(getattr(self, Properties._INNER_))
