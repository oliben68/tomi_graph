from abc import ABC, abstractmethod
from enum import Enum


class Category(Enum):
    NONE = 0
    _CORE = 1
    NODE = 2
    RELATIONSHIP = 4
    INDEX = 8
    GRAPH = 16


class BaseGraphEntity(ABC):
    category = Category._CORE

    @abstractmethod
    def to_graph(self):
        raise NotImplementedError
