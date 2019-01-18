from enum import Enum


class Signals(Enum):
    ENTITY_CREATED = "entity created"
    ENTITY_VALIDATED = "entity validated"
    ENTITY_CLONED = "entity cloned"
    ENTITY_UPDATED = "entity updated"
    UNKNOWN = "unknown"
