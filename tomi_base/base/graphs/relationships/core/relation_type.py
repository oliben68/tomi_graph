from enum import Enum


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
