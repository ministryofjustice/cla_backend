from collections import defaultdict
from .constants import LOG_LEVELS, LOG_TYPES, LOG_ROLES


def is_code_valid(code):
    required_keys = {
        'type': basestring,
        'level': int,
        'selectable_by': list,
        'description': basestring
    }

    for key, type_ in required_keys.items():
        if not key in code:
            raise ValueError('%s is missing from code definition' % key)
        if not isinstance(code[key], type_):
            raise ValueError('%s is not of expected type: %s' % (key, type_))

    if code['type'] not in LOG_TYPES.CHOICES_DICT:
        raise ValueError('Unknown type %s (must be one of %s)' % (code['type'], ', '.join(LOG_TYPES.CHOICES_DICT)))

    if code['level'] not in LOG_LEVELS.CHOICES_DICT:
        raise ValueError('Unknown level %s (must be one of %s)' % (code['level'], ', '.join([str(level) for level in LOG_LEVELS.CHOICES_DICT])))

    for selectable_by in code['selectable_by']:
        if selectable_by not in LOG_ROLES.CHOICES_DICT:
            raise ValueError('Unknown role %s (must be one of %s)' % (selectable_by, ', '.join(map(str, LOG_ROLES.CHOICES_DICT))))

    return True


class EventRegistry(object):
    def __init__(self):
        self._registry = {}

    def register(self, EventClazz):
        # checking that codes is not empty
        if not EventClazz.codes:
            raise ValueError('%s does not define any codes. Please add codes={} to the class' % EventClazz.__name__)

        if not EventClazz.key:
            raise ValueError('%s does not define any key. Please add key=\'<action-key>\' to the class' % EventClazz.__name__)

        # checking that each code in codes has the right format
        for code in EventClazz.codes.values():
            is_code_valid(code)

        self._registry[EventClazz.key] = EventClazz

    def get_event(self, key):
        if key not in self._registry:
            raise ValueError(u'%s not registered' % key)
        return self._registry[key]

    def get_selectable_events(self, role):
        events = defaultdict(list)

        for action_key, EventClazz in self._registry.items():
            selectable_codes = EventClazz.get_selectable_codes(role)
            if selectable_codes:
                events[action_key] = selectable_codes
        return events

event_registry = EventRegistry()
