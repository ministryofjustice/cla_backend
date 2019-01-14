from collections import OrderedDict

from cla_eventlog.models import Log
from cla_eventlog.constants import LOG_TYPES

from timer.utils import get_timer


# These are util functions that help Events set the right value of
#   `set_requires_action_by` quickly.
# Choose one of them if you want something else than a simple single value


def None_if_owned_by_operator(case):
    if case.requires_action_by_operator:
        return None
    return case.requires_action_by


def None_if_owned_by_op_or_op_manager(case):
    if case.requires_action_by_operator:
        return None
    if case.requires_action_by_operator_manager:
        return None
    return case.requires_action_by


class BaseEvent(object):
    """
    Subclass this when defining new events.
    E.g.

        class MyEvent(BaseEvent):
            key = 'my_key'
            codes = {
                'CODE1': {
                    'type': LOG_TYPES.OUTCOME,
                    'level': LOG_LEVELS.HIGH,
                    'selectable_by': [LOG_ROLES.OPERATOR],
                    'description': 'My description',
                    'stops_timer': True,
                    'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
                },
                'CODE2': {
                    'type': LOG_TYPES.OUTCOME,
                    'level': LOG_LEVELS.HIGH,
                    'selectable_by': [],
                    'description': 'My description',
                    'stops_timer': False
                },
            }

            def get_log_code(self, case=None, **kwargs):
                my_param = kwargs.get('my_param')
                if my_param == 'something':
                    return 'CODE1'
                return 'CODE2'
        event_registry.register(MyEvent)


    Code definition:
        '<code>': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.OPERATOR],
            'description': 'My description',
            'order': 1,
            'stops_timer': True,
            'set_requires_action_by': REQUIRES_ACTION_BY.OPERATOR
        }

        where:
            type: event type, see cla_eventlog.constants.LOG_TYPES
            level: event level, see cla_eventlog.constants.LOG_LEVELS
            selectable_by: not currently used
            order (optional): if set, the codes will be sorted when requesting
                the list `MyEvent.get_ordered_codes()`
            stops_timer: if True, it stops the running timer / time
                becomes billable
            set_requires_action_by (optional): sets the case.requires_action_by
                value to this

    Event registration:
        This is the only line you would need to add to register the event:
            event_registry.register(MyEvent)

    Usage:
        event = event_registry.get_event('my_key')  # get the event
        event.process(...)  # process the event.

        In most of the cases though, you would use a Form which does
        all of this for you

    Behaviour:
        Depends on the type of Event:
            One code event:
                If your event defines only one code, you don't need to add
                any extra logic.

            selectable code event:
                If your event defines more than one code and you allow the
                client to choose which one to use,
                then you don't need to add any extra logic.
                The choosen code will be passed to the .process method using
                the form.

            implicit code event:
                If your event defines more than one code and the logic behind
                which one to use is determined by the system.
                In this case you would need to define a
                `def get_log_code(self, case=None, **kwargs)` method and use
                a custom kwarg to determine which code to use.

    In plain words, when creating a new Event, most of the time you will have to:
        - Subclass BaseEvent
        - define .codes
        - define get_log_code if needed (only if the code to be used
            is choosen by the system)
        - register the event
        - use one of the cla_eventlog.forms depending on the type of Event
    """

    key = ""
    codes = {}

    @classmethod
    def get_ordered_codes(cls):
        if not hasattr(cls, "_ordered_codes"):
            cls._ordered_codes = OrderedDict(sorted(cls.codes.items(), key=lambda code: code[1].get("order", 10000)))
        return cls._ordered_codes

    def get_log_code(self, **kwargs):
        """
        Subclass this if you want to system to determine which code to use.
        If your event has only one code or you allow the client to choose the
        code to use, then you don't need to override this.
        """
        if len(self.codes) > 1:
            raise NotImplementedError()

        return self.codes.keys()[0]

    def save_log(self, log):
        log.save(force_insert=True)

    def create_log(self, *args, **kwargs):
        return Log(*args, **kwargs)

    def process(self, case, code=None, notes="", created_by=None, patch=None, context=None, **kwargs):
        """
        Processes the event and creates a log entry.
        """
        if not code:
            code = self.get_log_code(case=case, **kwargs)

        code_data = self.codes[code]
        timer = get_timer(created_by)

        log = self.create_log(
            case=case,
            code=code,
            timer=timer,
            type=code_data["type"],
            level=code_data["level"],
            notes=notes,
            patch=patch,
            created_by=created_by,
            context=context,
        )

        self.save_log(log)

        # stop timer if the code wants
        if timer and code_data.get("stops_timer", False):
            timer.stop()

        # update set_requires_action_by if the code wantes
        if "set_requires_action_by" in code_data:
            set_requires_action_by = code_data["set_requires_action_by"]
            if callable(set_requires_action_by):
                set_requires_action_by = set_requires_action_by(case)
            case.set_requires_action_by(set_requires_action_by)

        return log

    @classmethod
    def get_selectable_codes(cls, role):
        """
        Not currently used.
        """
        selectable_codes = []

        for code, code_data in cls.codes.items():
            if code_data["type"] == LOG_TYPES.OUTCOME and role in code_data["selectable_by"]:
                selectable_codes.append(code)
        return selectable_codes
