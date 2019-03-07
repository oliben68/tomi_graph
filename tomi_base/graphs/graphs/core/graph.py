from abc import abstractmethod

from tomi_base.graphs.base_graph_entity import BaseGraphEntity
from tomi_base.graphs.entity_category import EntityCategory


class BaseGraph(BaseGraphEntity):
    category = EntityCategory.GRAPH

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def relationships(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def nodes(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def namespace_root(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def namespace_map(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def namespace_delimiter(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def isolates(self):
        raise NotImplementedError

    @abstractmethod
    def add_node(self, entity):
        pass

    @abstractmethod
    def add_relationship(self, relationship):
        pass

    @abstractmethod
    def add_graph(self, graph):
        pass

    @abstractmethod
    def subtract_node(self, entity):
        pass

    @abstractmethod
    def subtract_relationship(self, relationship):
        pass

    @abstractmethod
    def subtract_graph(self, graph):
        pass

    @abstractmethod
    def search_relationships(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def search_entities(self, **kwargs):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def erase(self, obj):
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        raise NotImplementedError

    def toDict(self):
        return dict(__nodes={k: v.toDict() for k, v in self.nodes.items()},
                    __relationships=[r.toDict() for r in self.relationships],
                    __namespace_map=self.namespace_map)

    def to_graph(self):
        return self
