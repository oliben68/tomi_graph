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

    @abstractmethod
    def __str__(self):
        pass

    @staticmethod
    @abstractmethod
    def fromStr(string_value):
        pass

    def toDict(self):
        o = self.get_document()
        if issubclass(type(o), BaseDocument):
            doc = {"__type": "BaseDocument", "__object": o.toDict()}
        elif type(o) in BUILT_INS:
            doc = o
        else:
            try:
                doc = loads(dumps(self.get_document()))
            except:
                doc = o

        return {
            "core_id": self.core_id,
            "name": self._name,
            "key": str(self.key) if self.key is not None else None,
            "encoding": self.encoding,
            "document": doc
        }
