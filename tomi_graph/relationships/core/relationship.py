from abc import abstractmethod

from tomi_graph.base_graph_entity import GraphEntity
from tomi_graph.entity_category import EntityCategory


class CoreRelationshipClass(GraphEntity):
    category = EntityCategory.RELATIONSHIP

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def data(self):
        raise NotImplementedError

    @data.setter
    @abstractmethod
    def data(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def rel_type(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def node_1(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def node_2(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def direction(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def protection(self):
        raise NotImplementedError

    @abstractmethod
    def __init__(self, node_1, node_2, rel_type=None, direction=None, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def __reset__(self):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, name=None, rel_type=None, data=None):
        raise NotImplementedError

    def set(self, name=None, rel_type=None, data=None):
        return self.__call__(name=name, rel_type=rel_type, data=data)

    def __(self, name=None, rel_type=None, data=None):
        return self.__call__(name=name, rel_type=rel_type, data=data)
