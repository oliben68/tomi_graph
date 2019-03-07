import weakref
from collections.abc import MutableMapping
from copy import deepcopy
from enum import Enum
from uuid import uuid4

from tomi_base.graphs.entity_class_generator import EntityClassGenerator
from tomi_base.graphs.graphs.graph import Graph
from tomi_base.graphs.indexes_support import IndexesSupport
from tomi_base.graphs.nodes.core.node import CoreNodeClass
from tomi_base.graphs.operators import GraphOperationDirection, GraphOperation
from tomi_base.graphs.operators.operator_resolver import OperatorsResolver
from tomi_base.graphs.relationships.core.direction import Direction
from tomi_base.graphs.relationships.core.protection import Protection
from tomi_base.graphs.relationships.core.relation_type import RelationType
from tomi_base.graphs.relationships.core.relationship import CoreRelationshipClass
from tomi_base.graphs.relationships.exceptions import CoreRelationshipException
from tomi_base.graphs.version_aware_entity import VersionAwareEntity


class RelationshipBaseClass(OperatorsResolver, CoreRelationshipClass):
    def clone(self, new=None):
        return deepcopy(self)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if type(value) == str:
            self._name = value
        else:
            raise CoreRelationshipException("name property is of type str!")

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def rel_type(self):
        return type(self).__name__

    def return_entity_value(self, attribute_name):
        if getattr(self, attribute_name, None) is None:
            return None
        entity = getattr(self, attribute_name, None)()
        if entity is None:
            if attribute_name[1:] in self._safe.keys():
                return self._safe[attribute_name[1:]]
            return None
        return entity

    @property
    def node_1(self):
        if self._node_1 is None:
            return None
        return self._node_1()

    @property
    def node_2(self):
        if self._node_2 is None:
            return None
        return self._node_2()

    @property
    def direction(self):
        return self._direction

    @property
    def protection(self):
        return self._protection

    @property
    def unique_index(self):
        return ":".join([type(self).__name__, self._id])

    def to_graph(self):
        graph = Graph(Graph.NAMESPACE_DELIMITER)
        graph.add_relationship(self)

        return graph

    def __init__(self, node_1, node_2, name=None, direction=None, protection=None, **data):
        self._id = str(uuid4())
        self._name = str(name) if name is not None else None
        self._version = 0
        self._node_1 = weakref.ref(node_1)
        self._node_2 = weakref.ref(node_2)
        self._protection = protection if type(protection) == Protection else Protection.NONE
        self._rel_type = type(self).__name__
        self._direction = direction if type(direction) == Direction else Direction.NONE
        self._data = data

    def toDict(self):
        def value(v):
            if issubclass(type(v), Enum):
                return v.name
            elif type(v) == weakref.ReferenceType:
                entity = v()
                return entity.toDict() if issubclass(type(entity), CoreNodeClass) else None
            else:
                return v

        return {"_" + k: value(v) for k, v in self.__dict__.items()}

    def __repr__(self):

        return repr(self.toDict())

    def __str__(self):
        return str(self.toDict())

    def __call__(self, name=None, rel_type=None, data=None):
        if rel_type is not None and type(rel_type) == str:
            relationship_class = EntityClassGenerator(RelationshipBaseClass, VersionAwareEntity,
                                                      IndexesSupport).create(entity_type=rel_type)
            data = data if data is not None else self._data
            new_relationship = relationship_class(self.node_1, self.node_2, name=self.name, direction=self.direction,
                                                  protection=self.protection, **data)
            print("*" * 80)
            print(new_relationship.rel_type)
            print("*" * 80)

            return new_relationship
        else:
            self._rel_type = self._rel_type if rel_type is None or type(rel_type) not in [
                str, RelationType] else rel_type
            self._data = self._data if not isinstance(data, MutableMapping) else data
            self._name = str(name) if name is not None else self._name

            return self

    def __reset__(self):
        self._id = None
        self._node_1 = None
        self._node_2 = None
        self._safe = {}
        self._direction = Direction.NONE
        self(name=None, rel_type=RelationType.NONE, data={})

    def operation_resolution(self, other, operation, direction):
        if operation == GraphOperation.LINK:
            operator = "-"
            if direction == GraphOperationDirection.RELATIONSHIP_ENTITY:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_node(self.node_1)
                graph.add_node(self.node_2)
                graph.add_node(other)
                graph.add_relationship(self)
                graph.add_relationship(RelationshipBaseClass(self.node_2, other))
                return graph
            if direction == GraphOperationDirection.RELATIONSHIP_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_relationship(self)
                graph.add_relationship(other)
                graph.add_relationship(RelationshipBaseClass(self.node_2, other.node_1))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name__))
        if operation == GraphOperation.LINK_LEFT_RIGHT:
            operator = ">"
            if direction == GraphOperationDirection.RELATIONSHIP_ENTITY:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_node(self.node_1)
                graph.add_node(self.node_2)
                graph.add_node(other)
                graph.add_relationship(self)
                graph.add_relationship(RelationshipBaseClass(self.node_2, other, direction=Direction.LEFT_TO_RIGHT))
                return Graph
            if direction == GraphOperationDirection.RELATIONSHIP_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_node(self.node_1)
                graph.add_node(self.node_2)
                graph.add_node(other.node_1)
                graph.add_node(other.node_2)
                graph.add_relationship(self)
                graph.add_relationship(other)
                graph.add_relationship(
                    RelationshipBaseClass(self.node_2, other.node_1, direction=Direction.LEFT_TO_RIGHT))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name__))
        if operation == GraphOperation.LINK_RIGHT_LEFT:
            operator = "<"
            if direction == GraphOperationDirection.RELATIONSHIP_ENTITY:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_node(self.node_1)
                graph.add_node(self.node_2)
                graph.add_node(other)
                graph.add_relationship(self)
                graph.add_relationship(RelationshipBaseClass(self.node_2, other, direction=Direction.RIGHT_TO_LEFT))
                return graph
            if direction == GraphOperationDirection.RELATIONSHIP_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_node(self.node_1)
                graph.add_node(self.node_2)
                graph.add_node(other.node_1)
                graph.add_node(other.node_2)
                graph.add_relationship(self)
                graph.add_relationship(other)
                graph.add_relationship(
                    RelationshipBaseClass(self.node_2, other.node_1, direction=Direction.RIGHT_TO_LEFT))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name__))


Relationship = EntityClassGenerator(RelationshipBaseClass, VersionAwareEntity, IndexesSupport).create()
