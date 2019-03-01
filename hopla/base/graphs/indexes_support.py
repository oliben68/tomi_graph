from abc import ABC
from collections.abc import MutableSequence


class IndexesSupport(ABC):
    INDEXES_CLASS_METHOD = "get_type_indexes"

    @property
    def unique_index(self):
        raise NotImplementedError

    @property
    def indexes(self):
        entity_indexes = {"UIDX_{type}".format(type=type(self).__name__): self.unique_index}
        get_type_indexes = getattr(type(self), IndexesSupport.INDEXES_CLASS_METHOD, None)
        if get_type_indexes is not None and callable(get_type_indexes):
            if len(get_type_indexes()) > 0:
                for idx, fields in get_type_indexes().items():
                    try:
                        if issubclass(type(fields), MutableSequence):
                            entity_indexes[idx] = ":".join([getattr(self, field, field) for field in fields])
                    except AttributeError:
                        continue
        return entity_indexes
