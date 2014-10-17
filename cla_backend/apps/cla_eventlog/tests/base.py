from core.tests.mommy_utils import make_user, make_recipe

from cla_common.constants import REQUIRES_ACTION_BY

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
        process_kwargs={}, dummy_case=None
    ):
        """
        Used to test the `process` call when there's only one possible implicit
        code available so you don't need to pass an explicit one as param.
        """
        event = event_registry.get_event(self.EVENT_KEY)()

        if not dummy_case:
            dummy_case = self.dummy_case

        # building process params and overridding potential ones through process_kwargs
        _process_kwargs = {
            'case': dummy_case,
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
                created_by=_process_kwargs['created_by'],
            )
        )

    def _test_process_with_expicit_code_and_requires_action_None_if_operator(
        self, expected_available_codes,
        expected_type=LOG_TYPES.OUTCOME, expected_level=LOG_LEVELS.HIGH,
        process_kwargs={}, code=None
    ):

        # if `case.requires_action_by` is not Operator then the
        # value shouldn't change
        values = REQUIRES_ACTION_BY.REVERTED_CHOICES_CONST_DICT.keys()
        values.remove(REQUIRES_ACTION_BY.OPERATOR)

        for value in values:
            self.dummy_case.set_requires_action_by(value)
            self._test_process_with_expicit_code(
                expected_available_codes,
                expected_type=expected_type, expected_level=expected_level,
                process_kwargs=process_kwargs, code=code
            )

            case = Case.objects.get(pk=self.dummy_case.pk)
            self.assertEqual(case.requires_action_by, value)

        # if `case.requires_action_by` == Operator, then the value should
        # change to None
        self.dummy_case.set_requires_action_by(REQUIRES_ACTION_BY.OPERATOR)
        self._test_process_with_expicit_code(
            expected_available_codes,
            expected_type=expected_type, expected_level=expected_level,
            process_kwargs=process_kwargs, code=code
        )

        case = Case.objects.get(pk=self.dummy_case.pk)
        self.assertEqual(case.requires_action_by, None)

    def _test_process_with_expicit_code(
        self, expected_available_codes,
        expected_type=LOG_TYPES.OUTCOME, expected_level=LOG_LEVELS.HIGH,
        process_kwargs={}, code=None
    ):
        event = event_registry.get_event(self.EVENT_KEY)()
        codes = event.codes.keys()

        self.assertItemsEqual(codes, expected_available_codes)

        # building process params and overridding potential ones through process_kwargs
        chosen_code = code or codes[0]
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
                set_requires_action_by = code_data['set_requires_action_by']
                if callable(set_requires_action_by):
                    set_requires_action_by = set_requires_action_by(self.dummy_case)

                self.assertEqual(
                    case.requires_action_by, set_requires_action_by
                )
            else:
                self.assertEqual(case.requires_action_by, None)
