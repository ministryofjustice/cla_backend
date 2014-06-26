from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_ROLES, LOG_LEVELS
from cla_eventlog.models import Log
from core.tests.mommy_utils import make_user, make_recipe
from django.test import TestCase


class OutcomeEventsTestCase(TestCase):

    def setUp(self):
        self.dummy_case = make_recipe('legalaid.case')
        self.dummy_user =  make_user()

    def assertLogEqual(self, l1, l2):
        for attr in ['code', 'type', 'level', 'created_by', 'notes', 'case_id']:
            self.assertEqual(getattr(l1, attr), getattr(l2, attr))

    def test_assign_to_provider(self):
        event = event_registry.get_event('assign_to_provider')()

        # print "\ntesting manual allocation"
        res = event.process(self.dummy_case,
                            is_manual=True,
                            notes='this is a note',
                            created_by=self.dummy_user)

        self.assertLogEqual(res, Log(
            case=self.dummy_case,
            code='MANALC',
            type=LOG_TYPES.OUTCOME,
            notes='this is a note',
            level=LOG_LEVELS.HIGH,
            created_by=self.dummy_user))

        # print "\ntesting automatic allocation"
        res = event.process(self.dummy_case,
                            is_manual=False,
                            notes='this is a note2',
                            created_by=self.dummy_user)

        self.assertLogEqual(res, Log(
            code='REFSP',
            case=self.dummy_case,
            type=LOG_TYPES.OUTCOME,
            notes='this is a note2',
            created_by=self.dummy_user,
            level=LOG_LEVELS.HIGH))

    def test_defer_assignment(self):
        # defer assignment
        event = event_registry.get_event('defer_assignment')()
        # print "\ntesting defer assignment"
        res = event.process(self.dummy_case,
                            notes='defer note',
                            created_by=self.dummy_user)
        self.assertLogEqual(res, Log(
            case=self.dummy_case,
            code='CBSP',
            type=LOG_TYPES.OUTCOME,
            notes='defer note',
            created_by=self.dummy_user,
            level=LOG_LEVELS.HIGH
        ))

    def test_select_selectable_code(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role=LOG_ROLES.OPERATOR)

        for chosen_key, chosen_codes in selectable_events.items():
            for chosen_code in chosen_codes:
                # chosen key / code

                event = event_registry.get_event(chosen_key)()
                res = event.process(
                    self.dummy_case,
                    code=chosen_code,
                    notes='selectable notes',
                    created_by=self.dummy_user)

                self.assertLogEqual(res, Log(case=self.dummy_case,
                                             code=chosen_code,
                                             type=LOG_TYPES.OUTCOME,
                                             notes='selectable notes',
                                             level=LOG_LEVELS.HIGH,
                                             created_by=self.dummy_user))

    def test_select_selectable_code_invalid(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role='admin')
        self.assertEqual(selectable_events, {})

