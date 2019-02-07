from abc import ABC, abstractmethod

from hopla.base.graph import Category
from hopla.base.graph.core import Core


class BaseGraph(ABC, Core):
    category = Category.GRAPH

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
    def entities(self):
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
    def add_entity(self, entity):
        pass

    @abstractmethod
    def add_relationship(self, relationship):
        pass

    @abstractmethod
    def add_graph(self, graph):
        pass

    @abstractmethod
    def subtract_entity(self, entity):
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
        return dict(__entities={k: v.toDict() for k, v in self.entities.items()},
                    __relationships=[r.toDict() for r in self.relationships],
                    __namespace_map=self.namespace_map)
