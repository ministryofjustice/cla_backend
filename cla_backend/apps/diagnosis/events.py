from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.events import BaseEvent


class DiagnosisEvent(BaseEvent):
    key = "diagnosis"
    codes = {
        "DIAGNOSIS_CREATED": {
            "type": LOG_TYPES.SYSTEM,
            "level": LOG_LEVELS.HIGH,
            "selectable_by": [],
            "description": "Diagnosis created",
            "stops_timer": False,
        },
        "DIAGNOSIS_DELETED": {
            "type": LOG_TYPES.SYSTEM,
            "level": LOG_LEVELS.HIGH,
            "selectable_by": [],
            "description": "Diagnosis deleted",
            "stops_timer": False,
        },
        "INCOMPLETE_DIAGNOSIS_DELETED": {
            "type": LOG_TYPES.SYSTEM,
            "level": LOG_LEVELS.HIGH,
            "selectable_by": [],
            "description": "Incomplete Diagnosis deleted",
            "stops_timer": False,
        },
    }

    def get_log_code(self, **kwargs):
        status = kwargs["status"]
        lookup = {
            "created": "DIAGNOSIS_CREATED",
            "incomplete_deleted": "INCOMPLETE_DIAGNOSIS_DELETED",
            "deleted": "DIAGNOSIS_DELETED",
        }

        return lookup[status]


event_registry.register(DiagnosisEvent)
