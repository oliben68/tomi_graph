from tomi_graph.entity_class_generator import EntityClassGenerator
from tomi_graph.indexes.core.index import CoreIndex
from tomi_graph.nodes.core.node import CoreNodeClass
from tomi_graph.version_aware_entity import VersionAwareEntity


class IndexClass(CoreIndex):
    def __init__(self, node_type, field):
        if not issubclass(node_type, CoreNodeClass):
            raise TypeError("Node type must inherit from '{cls}'".format(cls=CoreNodeClass.__name__))

        self._node_type = node_type

        if not issubclass(field, str) or type(field) != property:
            raise TypeError("field must be either a string or a property")

        self._field = field if field is str else field.fget.__name__

    @property
    def node_type(self):
        return self._node_type

    @property
    def field(self):
        return self._field

    def to_graph(self):
        pass


Index = EntityClassGenerator(IndexClass, VersionAwareEntity)
