from enum import Enum


class Signals(Enum):
    DOCUMENT_CREATED = "document created"
    DOCUMENT_VALIDATED = "document validated"
    DOCUMENT_CLONED = "document cloned"
    DOCUMENT_UPDATED = "document updated"
    UNKNOWN = "unknown"
