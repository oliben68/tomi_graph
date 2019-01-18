from enum import Enum
from uuid import uuid4


class Direction(Enum):
    BIDIRECTIONAL = "bidirectional",
    LEFT_TO_RIGHT = "left_to_right",
    RIGHT_TO_LEFT = "right_to_left",
    NONE = None


class RelationType(Enum):
    CHILD = "child",
    PARENT = "parent",
    EMBEDDED = "embedded",
    STRONG = "strong",
    WEAK = "weak",
    REF = "ref",
    NONE = None

    @property
    def string(self):
        return self.name.upper()

    def upper(self):
        return self.string


class Protection(Enum):
    CASCADE_DELETE = "cascade_delete",
    PRESERVE = "preserve",
    NONE = None


NULL_VALUE = uuid4()
