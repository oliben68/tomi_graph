from uuid import uuid4

from hopla.base.graph import GraphOperation, GraphOperationDirection, DefaultValues
from hopla.base.graph.operator_resolver import OperatorsResolver
from hopla.entities.core.entity import BaseEntity
from hopla.graphs.core.graph import BaseGraph
from hopla.relationships.core.relationship import BaseRelationship


class Graph(OperatorsResolver, BaseGraph):
    NAMESPACE_DELIMITER = "/"

    @property
    def id(self):
        return self._id

    @property
    def relationships(self):
        return self._relationships

    @property
    def entities(self):
        return self._entities

    @property
    def namespace_root(self):
        return self._namespace_root

    @property
    def namespace_map(self):
        return self._namespace_map

    @property
    def namespace_delimiter(self):
        return Graph.NAMESPACE_DELIMITER

    @property
    def isolates(self):
        linked_entities = set(
            [core_id for sublist in [[r.entity_1.core_id, r.entity_2.core_id] for r in self.relationships] for core_id
             in sublist])
        return set([e.core_id for e in self.entities.values()]).difference(linked_entities)

    def __init__(self, namespace_root):
        self._id = str(uuid4())
        self._entities = {}
        self._relationships = []
        self._namespace_map = {}
        self._namespace_root = namespace_root

    def add_entity(self, entity, target=None):
        target = self if target is None else target
        target.entities[entity.core_id] = entity

    def add_relationship(self, relationship, target=None):
        target = self if target is None else target
        if relationship.id not in [r.id for r in target.relationships if r is not None]:
            target.add_entity(relationship.entity_1)
            target.add_entity(relationship.entity_2)
            target.relationships.append(relationship)

    def add_graph(self, graph, target=None):
        target = self if target is None else target

        if target.id != self.id:
            for relationship in self.relationships:
                target.add_relationship(relationship, target=target)

        for isolate in graph.isolates:
            target.add_entity(graph.entities[isolate], target=target)

        for relationship in graph.relationships:
            target.add_relationship(relationship, target=target)

        print("NAMSAPCE MPA", graph.namespace_map is not None and len(graph.namespace_map) > 0)
        if graph.namespace_map is not None and len(graph.namespace_map) > 0:
            target.namespace_map.update(graph.namespace_map)

        return target

    def subtract_entity(self, entity):
        if len(entity.graph.relationships) == 0 and len(entity.graph.entities) == 1:
            del self._entities[entity.core_id]
        else:
            self.subtract_graph(entity.graph)
        return self

    def subtract_relationship(self, relationship):
        # if relationship.id in self._relationships.keys():
        #     return  # TODO: throw warnings somewhere
        #
        # if len() > 0:
        #     return
        pass

    def subtract_graph(self, graph):
        pass

    def operation_resolution(self, other, operation, direction):
        if operation == GraphOperation.ADD:
            operator = "+"
            if direction == GraphOperationDirection.GRAPH_ENTITY:
                self.add_entity(other)
                return self
            if direction == GraphOperationDirection.GRAPH_RELATIONSHIP:
                self.add_relationship(other)
                return self
            if direction == GraphOperationDirection.GRAPH_GRAPH:
                return self.add_graph(other, target=Graph(Graph.NAMESPACE_DELIMITER))
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name,
                                                                                            other=type(other).__name))

        if operation == GraphOperation.SUB:
            operator = "-"
            if direction == GraphOperationDirection.GRAPH_ENTITY:
                self.subtract_entity(other)
                return self
            if direction == GraphOperationDirection.GRAPH_RELATIONSHIP:
                self.subtract_relationship(other)
                return self
            if direction == GraphOperationDirection.GRAPH_GRAPH:
                self.subtract_graph(other)
                return self
            raise TypeError(
                "Unsupported operand type(s) for {operator}: '{self}' and '{other}'".format(operator=operator,
                                                                                            self=type(self).__name,
                                                                                            other=type(other).__name))

    def search_relationships(self, **kwargs):
        # Defaults for search arguments: name=None, rel_type=None, protection=None, data=None, on_gc_collect=NULL_VAL
        search_arguments = {k: v for k, v in kwargs.items() if v != DefaultValues.RELATIONSHIP.value[k]}
        print(search_arguments)

    def search_entities(self, **kwargs):
        # Defaults for search arguments: entity_type=None, core_id=None, encoding=None, key=None, name=None, data=None,
        #   ttl=-1
        search_arguments = {k: v for k, v in kwargs.items() if v != DefaultValues.RELATIONSHIP.value[k]}
        print(search_arguments)

    @staticmethod
    def erase(self, obj):
        if issubclass(type(obj), BaseEntity):
            found = [k for k, e in self.entities.value_collection.items() if id(e) == id(obj)]
            if len(found) > 0:
                value = self.entities.get(found[0])()
                del value
                del self.entities[found[0]]

        if issubclass(type(obj), BaseRelationship):
            found = [r for r in self.relationships.value_collection if id(r) == id(obj)]
            if len(found) > 0:
                value = self.relationships.get(found[0])()
                del value
                del self.relationships[found[0]]

    def clear(self):
        self.entities.clear()
        self.relationships.clear()
        self._namespace_map = {}
