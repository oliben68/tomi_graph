from abc import ABC, abstractmethod
from collections.abc import MutableSequence


class IndexesSupport(ABC):
    INDEXES_CLASS_METHOD = "get_type_indexes"
    NULL_INDEX_VALUE = "null"
    UNIQUE_CONSTRAINT_PREFIX = "UQ"

    @classmethod
    def get_type_indexes(cls):
        pass

    @staticmethod
    def get_unique_constraint_name(entity_type):
        if issubclass(type(entity_type), type):
            entity_type_name = entity_type.__name__
        else:
            entity_type_name = entity_type if type(entity_type) == str else str(entity_type)

        return "{uq}_{type}".format(uq=IndexesSupport.UNIQUE_CONSTRAINT_PREFIX, type=entity_type_name)

    @staticmethod
    def create_unique_index(entity, fields):
        index_values = [getattr(entity, f, None) for f in fields]
        return ":".join([type(entity).__name__] + [str(value) if value is not None else "" for value in index_values])

    @property
    @abstractmethod
    def unique_index(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_unique_constraint_fields():
        raise NotImplementedError

    @property
    def indexes(self):
        def get_index_value(field):
            value = getattr(self, field, None)
            return str(value) if value is not None else IndexesSupport.NULL_INDEX_VALUE

        entity_indexes = {IndexesSupport.get_unique_constraint_name(type(self)): self.unique_index}

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
