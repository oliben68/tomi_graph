from enum import Enum


class Protection(Enum):
    CASCADE_DELETE = "cascade_delete",
    PRESERVE = "preserve",
    NONE = None
