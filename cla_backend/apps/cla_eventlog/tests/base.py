from core.tests.mommy_utils import make_user, make_recipe

from timer.models import Timer

from legalaid.models import Case

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS
from cla_eventlog.models import Log


class EventTestCaseMixin(object):
    EVENT_KEY = ''

    def setUp(self):
        self.dummy_case = make_recipe('legalaid.case')
        self.dummy_user = make_user()

    def assertLogEqual(self, l1, l2):
        for attr in ['code', 'type', 'level', 'created_by', 'notes', 'case_id', 'timer']:
            self.assertEqual(getattr(l1, attr), getattr(l2, attr))

    def _test_process_with_implicit_code(
        self, expected_code,
        expected_type=LOG_TYPES.OUTCOME, expected_level=LOG_LEVELS.HIGH,
        process_kwargs={}
    ):
        """
        Used to test the `process` call when there's only one possible implicit
        code available so you don't need to pass an explicit one as param.
        """
        event = event_registry.get_event(self.EVENT_KEY)()

        # building process params and overridding potential ones through process_kwargs
        _process_kwargs = {
            'case': self.dummy_case,
            'notes': 'this is a note',
            'created_by': self.dummy_user
        }
        _process_kwargs.update(process_kwargs)
        res = event.process(**_process_kwargs)

        # testing that everything worked
        self.assertLogEqual(
            res, Log(
                case=_process_kwargs['case'],
                code=expected_code,
                type=expected_type,
                notes=_process_kwargs['notes'],
                level=expected_level,
                created_by=_process_kwargs['created_by']
            )
        )

    def _test_process_with_expicit_code(
        self, expected_available_codes,
        expected_type=LOG_TYPES.OUTCOME, expected_level=LOG_LEVELS.HIGH,
        process_kwargs={}
    ):
        event = event_registry.get_event(self.EVENT_KEY)()
        codes = event.codes.keys()

        self.assertItemsEqual(codes, expected_available_codes)

        # building process params and overridding potential ones through process_kwargs
        chosen_code = codes[0]
        _process_kwargs = {
            'case': self.dummy_case,
            'code': chosen_code,
            'notes': 'this is a note',
            'created_by': self.dummy_user
        }
        _process_kwargs.update(process_kwargs)
        res = event.process(**_process_kwargs)

        # testing that everything worked
        self.assertLogEqual(
            res, Log(
                case=_process_kwargs['case'],
                code=_process_kwargs['code'],
                type=expected_type,
                notes=_process_kwargs['notes'],
                level=expected_level,
                created_by=_process_kwargs['created_by']
            )
        )

    def test_stops_timer(self):
        if not self.EVENT_KEY:
            return

        event = event_registry.get_event(self.EVENT_KEY)()

        for code, code_data in event.codes.items():
            user = make_user()
            timer = make_recipe('timer.Timer', created_by=user)

            res = event.process(**{
                'case': self.dummy_case,
                'code': code,
                'notes': 'this is a note',
                'created_by': user
            })

            timer = Timer.objects.get(pk=timer.pk)

            if code_data['stops_timer']:
                self.assertTrue(timer.is_stopped())
                self.assertEqual(res.timer, timer)
            else:
                self.assertFalse(timer.is_stopped())
                self.assertEqual(res.timer, timer)

    def test_set_requires_action_by(self):
        """
        Tests that:
            * if the code has the key `set_requires_action_by`,
                after process, case.requires_action_by will be set to
                that value
            * if the code doesn't have the key `set_requires_action_by`,
                after process, case.requires_action_by won't change
        """
        if not self.EVENT_KEY:
            return

        event = event_registry.get_event(self.EVENT_KEY)()

        for code, code_data in event.codes.items():
            self.dummy_case.requires_action_by = None
            self.dummy_case.save()
            user = make_user()

            event.process(**{
                'case': self.dummy_case,
                'code': code,
                'notes': 'this is a note',
                'created_by': user
            })

            case = Case.objects.get(pk=self.dummy_case.pk)

            if 'set_requires_action_by' in code_data:
                self.assertEqual(
                    case.requires_action_by,
                    code_data['set_requires_action_by']
                )
            else:
                self.assertEqual(case.requires_action_by, None)
