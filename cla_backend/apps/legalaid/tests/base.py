import mock

from rest_framework import status

from cla_common.constants import CASE_STATES, CASELOGTYPE_ACTION_KEYS

from legalaid.constants import CASELOGTYPE_SUBTYPES
from legalaid.models import Case
from cla_eventlog.models import Log

from core.tests.mommy_utils import make_recipe, make_user


def generate_outcome_codes():
    return [
        make_recipe('legalaid.outcome_code', code="CODE_OPEN",
            action_key='other'
        ),
        make_recipe('legalaid.outcome_code', code="CODE_ACCEPTED",
            action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_ACCEPT_CASE
        ),
        make_recipe('legalaid.outcome_code', code="CODE_REJECTED",
            action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_REJECT_CASE
        ),
        make_recipe('legalaid.outcome_code', code="CODE_CLOSED",
            action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE
        ),
        make_recipe('legalaid.outcome_code', code="CODE_DECLINED_ALL_SPECIALISTS",
            action_key=CASELOGTYPE_ACTION_KEYS.DECLINE_SPECIALISTS
        ),
        make_recipe('legalaid.logtype', code="CODE_LOGTYPE",
            subtype=CASELOGTYPE_SUBTYPES.SYSTEM
        )
    ]


class BaseStateFormTestCase(object):
    FORM = None,
    VALID_OUTCOME_CODE = None
    EXPECTED_CASE_STATE = None

    def setUp(self):
        super(BaseStateFormTestCase, self).setUp()

        self.user = make_user()

    def test_choices(self):
        form = self.FORM(case=mock.MagicMock())

        self.assertItemsEqual(
            [f[1] for f in form.fields['event_code'].choices], [self.VALID_OUTCOME_CODE]
        )

    def test_save_successfull(self):
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)

        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(Log.objects.count(), 0)

        form = self.FORM(case=case, data={
            'event_code': self.VALID_OUTCOME_CODE,
            'notes': 'lorem ipsum'
        })

        self.assertTrue(form.is_valid())

        form.save(self.user)

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, self.EXPECTED_CASE_STATE)

        self.assertEqual(Log.objects.count(), 1)
        outcome = Log.objects.all()[0]

        self.assertEqual(outcome.logtype.code, self.VALID_OUTCOME_CODE)
        self.assertEqual(outcome.notes, 'lorem ipsum')

    def test_invalid_form(self):
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)

        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(Log.objects.count(), 0)

        form = self.FORM(case=case, data={
            'event_code': 'invalid',
            'notes': 'l'*501
        })

        self.assertFalse(form.is_valid())

        self.assertItemsEqual(
            form.errors, {
                'event_code': [u'Select a valid choice. That choice is not one of the available choices.'],
                'notes': [u'Ensure this value has at most 500 characters (it has 501).']
            }
        )

        # nothing has changed
        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(Log.objects.count(), 0)


class StateChangeAPIMixin(object):
    VALID_OUTCOME_CODE = None
    EXPECTED_CASE_STATE = None
    INITIAL_CASE_STATE = CASE_STATES.OPEN
    INVALID_INITIAL_CASE_STATE = CASE_STATES.ACCEPTED

    def setUp(self):
        super(StateChangeAPIMixin, self).setUp()

        self.state_change_url = self.get_state_change_url()

    def get_state_change_url(self, reference=None):
        raise NotImplementedError()

    def test_methods_not_allowed(self):
        self._test_get_not_allowed(self.state_change_url)
        self._test_patch_not_allowed(self.state_change_url)
        self._test_delete_not_allowed(self.state_change_url)

    def test_invalid_reference(self):
        url = self.get_state_change_url(reference='invalid')

        response = self.client.post(url, data={},
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_401_if_not_logged_in(self):
        response = self.client.post(self.state_change_url, data={})
        self.assertTrue(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful(self):
        # before, case open and no outcomes
        self.assertEqual(self.check.state, self.INITIAL_CASE_STATE)

        self.assertEqual(Log.objects.count(), 0)

        # reject
        data={
                'event_code': self.VALID_OUTCOME_CODE,
                'notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # after, case rejected and outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, self.EXPECTED_CASE_STATE)

        self.assertEqual(Log.objects.count(), 1)
        outcome = Log.objects.all()[0]

        self.assertEqual(outcome.case, self.check)
        self.assertEqual(outcome.code, data['event_code'])
        self.assertEqual(outcome.notes, data['notes'])

    def test_invalid_outcome_code(self):
        # before, case open and no outcomes
        self.assertEqual(self.check.state, self.INITIAL_CASE_STATE)

        self.assertEqual(Log.objects.count(), 0)

        # reject
        data={
                'event_code': 'invalid',
                'notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'event_code': [u'Select a valid choice. invalid is not one of the available choices.']}
        )

        # after, case didn't change and no outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(Log.objects.count(), 0)

    def test_invalid_mutation(self):
        # before, case accepted and no outcomes
        self.check.state = self.INVALID_INITIAL_CASE_STATE
        self.check.save()
        self.assertEqual(self.check.state, self.INVALID_INITIAL_CASE_STATE)

        self.assertEqual(Log.objects.count(), 0)

        # reject
        data={
                'event_code': self.VALID_OUTCOME_CODE,
                'notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('case_state' in response.data)
        self.assertTrue('Case should be' in response.data['case_state'][0])

        # after, case didn't change and no outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, self.INVALID_INITIAL_CASE_STATE)

        self.assertEqual(Log.objects.count(), 0)


# NOTE: attempt to create a generic Mixin for API actions which create a log entry
# from events with only 1 code. Should be extended / changed including all other
# cases
class ViewActionWithSingleEventTestCase(object):
    def setUp(self):
        super(ViewActionWithSingleEventTestCase, self).setUp()
        self.url = self.get_url()

    def get_url(self, reference=None):
        raise NotImplementedError()

    def test_methods_not_allowed(self):
        self._test_get_not_allowed(self.url)
        self._test_patch_not_allowed(self.url)
        self._test_delete_not_allowed(self.url)

    def test_invalid_reference(self):
        url = self.get_url(reference='invalid')

        response = self.client.post(url, data={},
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_401_if_not_logged_in(self):
        response = self.client.post(self.url, data={})
        self.assertTrue(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful(self):
        # before, no logs
        self.assertEqual(Log.objects.count(), 0)

        data={
            'notes': 'lorem ipsum'
        }
        response = self.client.post(
            self.url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # after, log entry created
        # self.assertEqual(case.state, self.EXPECTED_CASE_STATE)
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]

        self.assertEqual(log.case, self.check)
        self.assertEqual(log.notes, data['notes'])
        self.assertEqual(log.created_by, self.user)
