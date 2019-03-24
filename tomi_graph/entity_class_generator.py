import inspect
from collections.abc import MutableMapping, Iterable

from tomi_base.shared.meta_singleton import MetaSingleton

from tomi_graph.indexes_support import IndexesSupport


class EntityClassRegistry(dict, metaclass=MetaSingleton):
    pass


class EntityClassGenerator(object):
    class_registry = EntityClassRegistry()

    def __init__(self, *base_classes):
        self.base_classes = base_classes

    def create(self, entity_type=None, indexes=None, additional_fields=None):
        if entity_type in EntityClassGenerator.class_registry.keys():
            entity_class = EntityClassGenerator.class_registry[entity_type]
            if set(self.base_classes).issubset(
                    set(inspect.getmro(entity_class))) and (entity_class.get_type_indexes() == indexes or (
                    entity_class.get_type_indexes() == {} and indexes is None)):
                return entity_class

        new_class = type(entity_type if type(entity_type) == str else self.base_classes[0].__name__,
                         self.base_classes, {})

        def valid_field(f):
            return f.split(":")[0] in self.base_classes[0].get_properties_mapping(node_type=entity_type).values()

        def idx_fields(cls):
            class_indexes = {}
            if issubclass(type(indexes), MutableMapping):
                for idx, fields in indexes.items():
                    valid_fields = [field for field in set(fields) if type(field) == str and valid_field(field)]
                    if len(valid_fields) > 0:
                        class_indexes[idx] = valid_fields
            return class_indexes

        setattr(new_class, IndexesSupport.INDEXES_CLASS_METHOD, classmethod(idx_fields))

        # registering additional fields
        if issubclass(type(additional_fields), Iterable) and type(additional_fields) != str:
            for field in [f for f in additional_fields if not hasattr(new_class, f)]:
                setattr(new_class, field, property(fget=lambda s: getattr(s, "_" + field, None),
                                                   fset=lambda s, v: setattr(s, "_" + field, v),
                                                   doc="Additional property '{name}'".format(name=field)))
            setattr(new_class, "additional_fields", additional_fields)

        EntityClassGenerator.class_registry[entity_type] = new_class

        return new_class
