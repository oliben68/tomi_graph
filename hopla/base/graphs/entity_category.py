from enum import Enum


class EntityCategory(Enum):
    NONE = 0
    _CORE = 1
    NODE = 2
    RELATIONSHIP = 4
    INDEX = 8
    GRAPH = 16
