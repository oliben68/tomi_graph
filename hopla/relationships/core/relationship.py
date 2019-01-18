from abc import ABC, abstractmethod


class BaseRelationship(ABC):
    @property
    @abstractmethod
    def id(self):
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

    @property
    @abstractmethod
    def safe(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def on_gc_collect(self):
        raise NotImplementedError

    @abstractmethod
    def __init__(self, entity_1, entity_2, rel_type=None, direction=None, protection=None, on_gc_collect=None,
                 **kwargs):
        raise NotImplementedError

    @abstractmethod
    def __reset__(self):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, rel_type=None, direction=None, protection=None):
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other):
        raise NotImplementedError
