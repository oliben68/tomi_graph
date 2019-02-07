from abc import ABC, abstractmethod

from hopla.graphs.category import Category

from hopla.graphs.core import Core


class BaseRelationship(Core, ABC):
    category = Category.RELATIONSHIP

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
    def entity_1(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def entity_2(self):
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
    def __init__(self, entity_1, entity_2, rel_type=None, direction=None, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def __reset__(self):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, name=None, data=None):
        raise NotImplementedError

