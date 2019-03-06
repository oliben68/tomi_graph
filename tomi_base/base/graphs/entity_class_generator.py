import inspect
from collections.abc import MutableMapping
from tomi_base.base.graphs.indexes_support import IndexesSupport
from tomi_base.base.shared.meta_singleton import MetaSingleton


class EntityClassRegistry(dict, metaclass=MetaSingleton):
    pass


class EntityClassGenerator(object):
    class_registry = EntityClassRegistry()

    def __init__(self, *base_classes):
        self.base_classes = base_classes

    def create(self, entity_type=None, indexes=None):
        if entity_type in EntityClassGenerator.class_registry.keys():
            entity_class = EntityClassGenerator.class_registry[entity_type]
            if set(self.base_classes).issubset(
                    set(inspect.getmro(entity_class))) and (entity_class.get_type_indexes() == indexes or (
                    entity_class.get_type_indexes() == {} and indexes is None)):
                return entity_class

        new_class = type(entity_type if type(entity_type) == str else self.base_classes[0].__name__,
                         self.base_classes, {})

        def valid_field(f):
            return f.split(":")[0] in self.base_classes[0].properties_mapping.values()

        def idx_fields(cls):
            class_indexes = {}
            if issubclass(type(indexes), MutableMapping):
                for idx, fields in indexes.items():
                    valid_fields = [field for field in set(fields) if type(field) == str and valid_field(field)]
                    if len(valid_fields) > 0:
                        class_indexes[idx] = valid_fields
            return class_indexes

        setattr(new_class, IndexesSupport.INDEXES_CLASS_METHOD, classmethod(idx_fields))

        EntityClassGenerator.class_registry[entity_type] = new_class

        return new_class
