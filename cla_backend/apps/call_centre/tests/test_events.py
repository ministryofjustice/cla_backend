from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_ROLES
from django.test import TestCase

class OutcomeEventsTestCase(TestCase):
    def test_assign_to_provider(self):
        event = event_registry.get_event('assign_to_provider')()

        # print "\ntesting manual allocation"
        res = event.process(is_manual=True, notes='this is a note')
        self.assertEqual(res, ('MANALC', LOG_TYPES.OUTCOME, 'this is a note'))

        # print "\ntesting automatic allocation"
        res = event.process(is_manual=False, notes='this is a note2')
        self.assertEqual(res, ('REFSP', LOG_TYPES.OUTCOME, 'this is a note2'))

    def test_defer_assignment(self):
        # defer assignment
        event = event_registry.get_event('defer_assignment')()
        # print "\ntesting defer assignment"
        res = event.process(notes='defer note')
        self.assertEqual(res, ('CBSP', LOG_TYPES.OUTCOME, 'defer note'))

    def test_select_selectable_code(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role=LOG_ROLES.OPERATOR)

        for chosen_key, chosen_codes in selectable_events.items():
            for chosen_code in chosen_codes:
                # chosen key / code

                event = event_registry.get_event(chosen_key)()
                res = event.process(code=chosen_code, notes='selectable notes')
                self.assertEqual(res, (chosen_code, LOG_TYPES.OUTCOME, 'selectable notes'))

    def test_select_selectable_code_invalid(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role='admin')
        self.assertEqual(selectable_events, {})

