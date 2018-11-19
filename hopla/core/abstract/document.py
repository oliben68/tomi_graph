from abc import ABC, abstractmethod
from ujson import dumps, loads

from hopla.core.abstract import BUILT_INS


class BaseDocument(ABC):
    @property
    @abstractmethod
    def core_id(self):
        pass

    @core_id.setter
    @abstractmethod
    def core_id(self, value):
        pass

    @property
    @abstractmethod
    def key(self):
        pass

    @key.setter
    @abstractmethod
    def key(self, value):
        pass

    @property
    @abstractmethod
    def encoding(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @name.setter
    @abstractmethod
    def name(self, value):
        pass

    @property
    @abstractmethod
    def options(self):
        pass

    @abstractmethod
    def set_document(self, value):
        pass

    @abstractmethod
    def get_document(self):
        pass

    @abstractmethod
    def validate(self, document):
        pass

    @staticmethod
    def clone(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @property
    @abstractmethod
    def create_date(self):
        pass

    @property
    @abstractmethod
    def update_date(self):
        pass

    @staticmethod
    def fromStr(string_value, clone=None):
        pass

    @abstractmethod
    def toDict(self):
        pass
