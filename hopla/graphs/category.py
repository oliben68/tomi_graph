from enum import Enum


class Category(Enum):
    NONE = 0
    _CORE = 1
    ENTITY = 2
    RELATIONSHIP = 4
    INDEX = 8
    GRAPH = 16
