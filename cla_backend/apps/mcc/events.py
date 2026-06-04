from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.events import BaseEvent


class ChangeCategoryEvent(BaseEvent):
    """
    Custom event for MCC to log category changes
    """
    key = "change_category"

    codes = {
        "MCC": {
            "type": LOG_TYPES.OUTCOME,
            "level": LOG_LEVELS.HIGH,
            "selectable_by": [],
            "description": "Category changed via MCC",
            "stops_timer": False,
        }
    }


event_registry.register(ChangeCategoryEvent)
