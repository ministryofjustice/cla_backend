from django.test import TestCase

from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.events import BaseEvent
from cla_eventlog.registry import EventRegistry


#
# class SystemEventsTestCase(TestCase):
#     def test_means_test_events(self):
#         event = event_registry.get_event('means_test')()
#
#         # means test created
#         res = event.process(status='created', notes='means test created')
#         self.assertEqual(res, ('MT_CREATED', LOG_TYPES.SYSTEM, 'means test created'))
#
#         # means test changed
#         res = event.process(status='changed', notes='Notes field changed from xxx to yyy')
#         self.assertEqual(res, ('MT_CHANGED', LOG_TYPES.SYSTEM, 'Notes field changed from xxx to yyy'))
#
#         # means test passed
#         res = event.process(status='passed', notes='Means test passed')
#         self.assertEqual(res, ('MT_PASSED', LOG_TYPES.SYSTEM, 'Means test passed'))
#
#         # means test failed
#         res = event.process(status='failed', notes='Means test failed')
#         self.assertEqual(res, ('MT_FAILED', LOG_TYPES.SYSTEM, 'Means test failed'))
#
#     def test_case_events(self):
#         event = event_registry.get_event('case')()
#
#         # case created digitally
#         res = event.process(status='created', notes='Case created digitally')
#         self.assertEqual(res, ('CASE_CREATED', LOG_TYPES.SYSTEM, 'Case created digitally'))
#
#         # case created NOT digitally
#         res = event.process(status='created', notes='Case created')
#         self.assertEqual(res, ('CASE_CREATED', LOG_TYPES.SYSTEM, 'Case created'))
#
#         # case viewed
#         res = event.process(status='viewed', notes='Case viewed')
#         self.assertEqual(res, ('CASE_VIEWED', LOG_TYPES.SYSTEM, 'Case viewed'))


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
