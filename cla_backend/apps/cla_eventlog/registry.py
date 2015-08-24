from collections import defaultdict
import operator
from .constants import LOG_LEVELS, LOG_TYPES, LOG_ROLES


def is_code_valid(code):
    required_keys = {
        'type': basestring,
        'level': int,
        'selectable_by': list,
        'description': basestring,
        'stops_timer': bool
    }
    all_keys = required_keys.keys() + ['set_requires_action_by', 'order']

    for key, type_ in required_keys.items():
        if key not in code:
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

    diff = set(code.keys()) - set(all_keys)
    if len(diff) > 0:
        raise ValueError('Unknown key(s) %s (must be one of %s)' % (diff, all_keys))

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

    def all(self):
        """
        :return: all codes in the registry as a unified dictionary
        """
        return dict(reduce(operator.add, [EventClazz.codes.items() for EventClazz in self._registry.values()]))

    def filter(self, **kwargs):
        """
        Similar to Django's models.objects.filter(...) this will filter
        all of the codes in the system by the kwargs passed into this
        function.

        For example,
        >> registry.filter(stops_timer=True)
        would return all codes in the system that stop the timer. You can
        supply multiple kwargs, so if you wanted to see all codes which
        are of type 'OUTCOME' and don't stop the timer you can do this:
        >> registry.filter(stops_timer=False, type=LOG_TYPES.OUTCOME)


        :param kwargs: set of keyword args you want to filter the outcome
        codes by
        :return: returns a unified dictionary of filtered outcome codes
        registered in this registry.
        """
        return {k: v for k, v in self.all().items() if
                all([v[kk]==vv for kk,vv in kwargs.items()])}


event_registry = EventRegistry()
