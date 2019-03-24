from enum import Enum


class EntityCategory(Enum):
    NONE = 0
    CORE = 1
    NODE = 2
    RELATIONSHIP = 4
    INDEX = 8
    GRAPH = 16
    CONSTRAINT = 32
