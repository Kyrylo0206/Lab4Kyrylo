from enum import Enum

class PriorityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class EventTypeEnum(str, Enum):
    TODO_CREATED = "TODO_CREATED"
    TODO_UPDATED = "TODO_UPDATED"
    TODO_DELETED = "TODO_DELETED"