from core.tests.mommy_utils import make_user, make_recipe

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.models import Log


class EventTestCaseMixin(object):
    def setUp(self):
        self.dummy_case = make_recipe('legalaid.case')
        self.dummy_user =  make_user()

    def assertLogEqual(self, l1, l2):
        for attr in ['code', 'type', 'level', 'created_by', 'notes', 'case_id']:
            self.assertEqual(getattr(l1, attr), getattr(l2, attr))

    def _test_process_event_key_with_one_code(self, event_key, expected_code,
        expected_type=LOG_TYPES.OUTCOME, expected_level=LOG_LEVELS.HIGH,
        process_kwargs={}
    ):
        event = event_registry.get_event(event_key)()


        _process_kwargs = {
            'case': self.dummy_case,
            'notes': 'this is a note',
            'created_by': self.dummy_user
        }
        _process_kwargs.update(process_kwargs)
        res = event.process(**_process_kwargs)

        self.assertLogEqual(res, Log(
                case=_process_kwargs['case'],
                code=expected_code,
                type=expected_type,
                notes=_process_kwargs['notes'],
                level=expected_level,
                created_by=_process_kwargs['created_by']
            )
        )

