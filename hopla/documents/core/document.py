from abc import ABC, abstractmethod


class BaseDocument(ABC):
    @property
    @abstractmethod
    def core_id(self):
        raise NotImplementedError

    @core_id.setter
    @abstractmethod
    def core_id(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def key(self):
        raise NotImplementedError

    @key.setter
    @abstractmethod
    def key(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def encoding(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @name.setter
    @abstractmethod
    def name(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def ttl(self):
        raise NotImplementedError

    @ttl.setter
    @abstractmethod
    def ttl(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def options(self):
        raise NotImplementedError

    @abstractmethod
    def set_document(self, value):
        raise NotImplementedError

    @abstractmethod
    def get_document(self):
        raise NotImplementedError

    @abstractmethod
    def validate(self, document):
        raise NotImplementedError

    @staticmethod
    def clone(self):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def create_date(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def update_date(self):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def from_str(string_value, clone=None):
        raise NotImplementedError

    @abstractmethod
    def toDict(self):
        """
        Support for custom serialization with ujson
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def children(self):
        raise NotImplementedError
