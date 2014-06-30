import mock

from rest_framework import status

from cla_common.constants import CASE_STATES, CASELOGTYPE_ACTION_KEYS

from cla_eventlog.models import Log

from legalaid.constants import CASELOGTYPE_SUBTYPES
from legalaid.models import CaseLog, Case

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


class BaseCaseLogFormTestCaseMixin(object):
    FORM = None

    def setUp(self):
        super(BaseCaseLogFormTestCaseMixin, self).setUp()

        self.user = make_user()

    def get_default_data(self):
        return {
            'notes': 'lorem ipsum'
        }

    def test_save_successfull(self):
        case = make_recipe('legalaid.case')
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_default_data()
        form = self.FORM(case=case, data=data)

        self.assertTrue(form.is_valid())

        form.save(self.user)

        case = Case.objects.get(pk=case.pk)

        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]

        self.assertEqual(log.notes, 'lorem ipsum')
        self.assertEqual(log.created_by, self.user)
        self.assertEqual(log.case, case)

    def test_invalid_form(self):
        case = make_recipe('legalaid.case')
        self.assertEqual(CaseLog.objects.count(), 0)

        data = self.get_default_data()
        data['notes'] = 'l'*501
        form = self.FORM(case=case, data=data)

        self.assertFalse(form.is_valid())

        self.assertItemsEqual(
            form.errors, {
                'notes': [u'Ensure this value has at most 500 characters (it has 501).']
            }
        )

        # nothing has changed
        case = Case.objects.get(pk=case.pk)
        self.assertEqual(CaseLog.objects.count(), 0)


class EventSpecificLogFormTestCaseMixin(BaseCaseLogFormTestCaseMixin):
    def get_default_data(self):
        data = super(EventSpecificLogFormTestCaseMixin, self).get_default_data()

        form = self.FORM(case=mock.MagicMock())
        event_code = form.fields['event_code'].choices[0][0]  # getting the first code
        data['event_code'] = event_code

        return data

    def test_invalid_event_code(self):
        # test with invalid code
        case = make_recipe('legalaid.case')
        self.assertEqual(CaseLog.objects.count(), 0)

        data = self.get_default_data()
        data['event_code'] = 'invalid'
        form = self.FORM(case=case, data=data)

        self.assertFalse(form.is_valid())

        self.assertItemsEqual(
            form.errors, {
                'event_code': [u'Invalid choice']
            }
        )


class StateChangeAPIMixin(object):
    VALID_OUTCOME_CODE = None
    EXPECTED_CASE_STATE = None
    INITIAL_CASE_STATE = CASE_STATES.OPEN
    INVALID_INITIAL_CASE_STATE = CASE_STATES.ACCEPTED

    def setUp(self):
        super(StateChangeAPIMixin, self).setUp()

        self.outcome_codes = generate_outcome_codes()
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

        self.assertEqual(CaseLog.objects.count(), 0)

        # reject
        data={
                'outcome_code': self.VALID_OUTCOME_CODE,
                'outcome_notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # after, case rejected and outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, self.EXPECTED_CASE_STATE)

        self.assertEqual(CaseLog.objects.count(), 1)
        outcome = CaseLog.objects.all()[0]

        self.assertEqual(outcome.case, self.check)
        self.assertEqual(outcome.logtype.code, data['outcome_code'])
        self.assertEqual(outcome.notes, data['outcome_notes'])

    def test_invalid_outcome_code(self):
        # before, case open and no outcomes
        self.assertEqual(self.check.state, self.INITIAL_CASE_STATE)

        self.assertEqual(CaseLog.objects.count(), 0)

        # reject
        data={
                'outcome_code': 'invalid',
                'outcome_notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'outcome_code': [u'Select a valid choice. That choice is not one of the available choices.']}
        )

        # after, case didn't change and no outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(CaseLog.objects.count(), 0)

    def test_invalid_mutation(self):
        # before, case accepted and no outcomes
        self.check.state = self.INVALID_INITIAL_CASE_STATE
        self.check.save()
        self.assertEqual(self.check.state, self.INVALID_INITIAL_CASE_STATE)

        self.assertEqual(CaseLog.objects.count(), 0)

        # reject
        data={
                'outcome_code': self.VALID_OUTCOME_CODE,
                'outcome_notes': 'lorem ipsum'
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

        self.assertEqual(CaseLog.objects.count(), 0)


class ImplicitEventCodeViewTestCaseMixin(object):
    """
    This is for endpoints which mainly create implicit outcome after
    an action (e.g. close case, accept case etc.).

    The user is not given the possibility to specify an outcome code.
    """
    def setUp(self):
        super(ImplicitEventCodeViewTestCaseMixin, self).setUp()
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

    def get_default_post_data(self):
        return {
            'notes': 'lorem ipsum'
        }

    def test_successful(self):
        # before, no logs
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_default_post_data()
        response = self.client.post(
            self.url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # after, log entry created
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]

        self.assertEqual(log.case, self.check)
        self.assertEqual(log.notes, data['notes'])
        self.assertEqual(log.created_by, self.user)


class ExplicitEventCodeViewTestCaseMixin(ImplicitEventCodeViewTestCaseMixin):
    """
    This is for endpoints which create explicit outcomes after
    an action (e.g. reject case etc.).

    The user is given the possibility to specify an outcome code from a list of
    valid ones.
    """
    def get_event_code(self):
        """
        Should return a __valid__ code for this endpoints.
        """
        raise NotImplementedError()

    def get_default_post_data(self):
        data = super(ExplicitEventCodeViewTestCaseMixin, self).get_default_post_data()
        data['event_code'] = self.get_event_code()
        return data
