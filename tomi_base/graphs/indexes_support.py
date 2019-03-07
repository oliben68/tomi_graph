from abc import ABC
from collections.abc import MutableSequence


class IndexesSupport(ABC):
    INDEXES_CLASS_METHOD = "get_type_indexes"
    NULL_INDEX_VALUE = "null"
    UNIQUE_CONSTRAINT_PREFIX = "UQ"

    @property
    def unique_index(self):
        raise NotImplementedError

    @property
    def indexes(self):
        def get_index_value(field):
            value = getattr(self, field, None)
            return str(value) if value is not None else IndexesSupport.NULL_INDEX_VALUE

        entity_indexes = {"{uq}_{type}".format(uq=IndexesSupport.UNIQUE_CONSTRAINT_PREFIX,
                                               type=type(self).__name__): self.unique_index}

        get_type_indexes = getattr(type(self), IndexesSupport.INDEXES_CLASS_METHOD, None)
        if get_type_indexes is not None and callable(get_type_indexes):
            if len(get_type_indexes()) > 0:
                for idx, fields in get_type_indexes().items():
                    try:
                        if issubclass(type(fields), MutableSequence):
                            entity_indexes[idx] = ":".join([get_index_value(field) for field in fields])
                    except (AttributeError, TypeError):
                        continue

        return entity_indexes
