import weakref
from enum import Enum
from uuid import uuid4

from hopla.graphs.graphs.graph import Graph

from hopla.graphs.operators import GraphOperationDirection, GraphOperation
from hopla.graphs.operators.operator_resolver import OperatorsResolver
from hopla.graphs.nodes.core.node import BaseNode
from hopla.graphs.relationships.core import Direction, RelationType, Protection
from hopla.graphs.relationships.core.relationship import BaseRelationship
from hopla.graphs.relationships.exceptions import CoreRelationshipException


class Relationship(OperatorsResolver, BaseRelationship):
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
        return self._rel_type

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
    def entity_1(self):
        if self._entity_1 is None:
            return None
        return self._entity_1()

    @property
    def entity_2(self):
        if self._entity_2 is None:
            return None
        return self._entity_2()

    @property
    def direction(self):
        return self._direction

    @property
    def protection(self):
        return self._protection

    def __init__(self, entity_1, entity_2, name=None, rel_type=None, direction=None, protection=None, **kwargs):
        self._id = str(uuid4())
        self._name = self._id if name is None else str(name)
        self._entity_1 = weakref.ref(entity_1)
        self._entity_2 = weakref.ref(entity_2)
        self._protection = protection if type(protection) == Protection else Protection.NONE
        self._rel_type = Relationship.__name__.upper() if rel_type is None or type(
            rel_type) != str else rel_type.upper()
        self._direction = direction if type(direction) == Direction else Direction.NONE
        self._data = kwargs

    def toDict(self):
        def value(v):
            if issubclass(type(v), Enum):
                return v.name
            elif type(v) == weakref.ReferenceType:
                entity = v()
                return entity.toDict() if issubclass(type(entity), BaseNode) else None
            else:
                return v

        return {"_" + k: value(v) for k, v in self.__dict__.items()}

    def __repr__(self):

        return repr(self.toDict())

    def __str__(self):
        return str(self.toDict())

    def __call__(self, name=None, rel_type=None, data=None):
        self._rel_type = self._rel_type if rel_type is None or type(rel_type) not in [
            str, RelationType] else rel_type.upper()
        self._data = data if data is None else self._data
        self._name = name if type(name) == str else self._name

        return self

    def __reset__(self):
        self._id = None
        self._entity_1 = None
        self._entity_2 = None
        self._safe = {}
        self._direction = Direction.NONE
        self(name=None, rel_type=RelationType.NONE, data={})

    def operation_resolution(self, other, operation, direction):
        if operation == GraphOperation.LINK:
            operator = "-"
            if direction == GraphOperationDirection.RELATIONSHIP_ENTITY:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self.entity_1)
                graph.add_entity(self.entity_2)
                graph.add_entity(other)
                graph.add_relationship(self)
                graph.add_relationship(Relationship(self.entity_2, other))
                return graph
            if direction == GraphOperationDirection.RELATIONSHIP_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_relationship(self)
                graph.add_relationship(other)
                graph.add_relationship(Relationship(self.entity_2, other.entity_1))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name))
        if operation == GraphOperation.LINK_LEFT_RIGHT:
            operator = ">"
            if direction == GraphOperationDirection.RELATIONSHIP_ENTITY:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self.entity_1)
                graph.add_entity(self.entity_2)
                graph.add_entity(other)
                graph.add_relationship(self)
                graph.add_relationship(Relationship(self.entity_2, other, direction=Direction.LEFT_TO_RIGHT))
                return Graph
            if direction == GraphOperationDirection.RELATIONSHIP_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self.entity_1)
                graph.add_entity(self.entity_2)
                graph.add_entity(other.entity_1)
                graph.add_entity(other.entity_2)
                graph.add_relationship(self)
                graph.add_relationship(other)
                graph.add_relationship(Relationship(self.entity_2, other.entity_1, direction=Direction.LEFT_TO_RIGHT))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name__,
                                                                                            other=type(other).__name))
        if operation == GraphOperation.LINK_RIGHT_LEFT:
            operator = "<"
            if direction == GraphOperationDirection.RELATIONSHIP_ENTITY:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self.entity_1)
                graph.add_entity(self.entity_2)
                graph.add_entity(other)
                graph.add_relationship(self)
                graph.add_relationship(Relationship(self.entity_2, other, direction=Direction.RIGHT_TO_LEFT))
                return graph
            if direction == GraphOperationDirection.RELATIONSHIP_RELATIONSHIP:
                graph = Graph(Graph.NAMESPACE_DELIMITER)
                graph.add_entity(self.entity_1)
                graph.add_entity(self.entity_2)
                graph.add_entity(other.entity_1)
                graph.add_entity(other.entity_2)
                graph.add_relationship(self)
                graph.add_relationship(other)
                graph.add_relationship(Relationship(self.entity_2, other.entity_1, direction=Direction.RIGHT_TO_LEFT))
                return graph
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name,
                                                                                            other=type(other).__name))
