from django.test import TestCase

from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.events import BaseEvent
from cla_eventlog.registry import EventRegistry


class RegistryStartupChecksTestCase(TestCase):
    def test_event_without_key_fails(self):
        registry = EventRegistry()

        class MyEvent(BaseEvent):
            codes = {
                'MY_CODE': {
                    'type': LOG_TYPES.SYSTEM,
                    'selectable_by': [],
                    'description': "my code"
                },
                }

        self.assertRaises(ValueError, registry.register, MyEvent)

    def test_event_without_codes_fails(self):
        registry = EventRegistry()

        class MyEvent(BaseEvent):
            key = 'case'

        self.assertRaises(ValueError, registry.register, MyEvent)

    def test_event_with_missing_code_key_fails(self):
        registry = EventRegistry()

        for missing_key in ['type', 'selectable_by', 'description']:
            _codes = {
                'MY_CODE': {
                    'type': LOG_TYPES.SYSTEM,
                    'level': LOG_LEVELS.HIGH,
                    'selectable_by': [],
                    'description': "my code"
                },
                }
            del _codes['MY_CODE'][missing_key]

            class MyEvent(BaseEvent):
                key = 'my_key'
                codes = _codes

            self.assertRaises(ValueError, registry.register, MyEvent)

    def test_event_with_wrong_type_code_key_fails(self):
        registry = EventRegistry()

        for wrong_type_key in ['type', 'selectable_by', 'description']:
            _codes = {
                'MY_CODE': {
                    'type': LOG_TYPES.SYSTEM,
                    'level': LOG_LEVELS.HIGH,
                    'selectable_by': [],
                    'description': "my code"
                },
                }
            _codes['MY_CODE'][wrong_type_key] = float(1)  # not really great but hey...

            class MyEvent(BaseEvent):
                key = 'my_key'
                codes = _codes

            self.assertRaises(ValueError, registry.register, MyEvent)

    def test_event_with_wrong_type_value_fails(self):
        registry = EventRegistry()

        _codes = {
            'MY_CODE': {
                'type': 'wrong-type',
                'level': LOG_LEVELS.HIGH,
                'selectable_by': [],
                'description': "my code"
            },
            }

        class MyEvent(BaseEvent):
            key = 'my_key'
            codes = _codes

        self.assertRaises(ValueError, registry.register, MyEvent)

    def test_event_with_wrong_level_value_fails(self):
        registry = EventRegistry()

        _codes = {
            'MY_CODE': {
                'type': LOG_TYPES.SYSTEM,
                'level': -1,
                'selectable_by': [],
                'description': "my code"
            },
            }

        class MyEvent(BaseEvent):
            key = 'my_key'
            codes = _codes

        self.assertRaises(ValueError, registry.register, MyEvent)

    def test_event_with_wrong_selected_by_fails(self):
        registry = EventRegistry()

        _codes = {
            'MY_CODE': {
                'type': LOG_TYPES.SYSTEM,
                'level': LOG_LEVELS.HIGH,
                'selectable_by': ['foo'],
                'description': "my code"
            },
            }

        class MyEvent(BaseEvent):
            key = 'my_key'
            codes = _codes

        self.assertRaises(ValueError, registry.register, MyEvent)

    def test_event_registry_all(self):

        registry = EventRegistry()

        _codes = {
            'MY_CODE': {
                'type': LOG_TYPES.SYSTEM,
                'level': LOG_LEVELS.HIGH,
                'selectable_by': [],
                'description': "my code",
                'stops_timer': True
            },
        }

        class MyEvent(BaseEvent):
            key = 'my_key'
            codes = _codes

        registry.register(MyEvent)

        res = registry.all()
        self.assertEqual(len(res), 1)
        self.assertTrue('MY_CODE' in res, res)

    def test_event_registry_filter(self):

        registry = EventRegistry()

        _codes = {
            'MY_CODE': {
                'type': LOG_TYPES.SYSTEM,
                'level': LOG_LEVELS.HIGH,
                'selectable_by': [],
                'description': "my code",
                'stops_timer': True
            },
            }

        class MyEvent(BaseEvent):
            key = 'my_key'
            codes = _codes

        registry.register(MyEvent)

        res = registry.all()
        self.assertEqual(len(res), 1)
        self.assertTrue('MY_CODE' in res, res)
        filt = registry.filter(stops_timer=False)
        self.assertEqual(len(filt), 0)
        self.assertFalse('MY_CODE' in filt, filt)
