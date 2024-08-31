from enum import Enum


class EventType(Enum):
    ERROR = 0
    UPDATE_UI_TREE_VIEW = 1
    UPDATE_UI_TASK_TIPS = 2


class NearExpiryType(Enum):
    SUCCESS = 0
    NO_NEED = 1
    ERROR = 2
