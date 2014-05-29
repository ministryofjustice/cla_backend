import mock

from rest_framework import status

from cla_common.constants import CASE_STATES, CASE_LOGTYPE_ACTION_KEYS

from legalaid.models import CaseLog, Case

from core.tests.mommy_utils import make_recipe, make_user


def generate_outcome_codes():
    return [
        make_recipe('legalaid.outcome_code', code="CODE_OPEN", case_state=CASE_STATES.OPEN),
        make_recipe('legalaid.outcome_code', code="CODE_ACCEPTED", case_state=CASE_STATES.ACCEPTED),
        make_recipe('legalaid.outcome_code', code="CODE_REJECTED", case_state=CASE_STATES.REJECTED),
        make_recipe('legalaid.outcome_code', code="CODE_CLOSED", case_state=CASE_STATES.CLOSED),
        make_recipe(
            'legalaid.outcome_code', code="CODE_DECLINED_ALL_SPECIALISTS",
            case_state=None, action_key=CASE_LOGTYPE_ACTION_KEYS.DECLINE_SPECIALISTS
        ),
    ]


class BaseStateFormTestCase(object):
    FORM = None,
    VALID_OUTCOME_CODE = None
    EXPECTED_CASE_STATE = None

    def setUp(self):
        super(BaseStateFormTestCase, self).setUp()

        self.user = make_user()
        self.outcome_codes = generate_outcome_codes()

    def test_choices(self):
        form = self.FORM(case=mock.MagicMock())

        self.assertItemsEqual(
            [f[1] for f in form.fields['outcome_code'].choices], [self.VALID_OUTCOME_CODE]
        )

    def test_save_successfull(self):
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)

        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(CaseLog.objects.count(), 0)

        form = self.FORM(case=case, data={
            'outcome_code': self.VALID_OUTCOME_CODE,
            'outcome_notes': 'lorem ipsum'
        })

        self.assertTrue(form.is_valid())

        form.save(self.user)

        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, self.EXPECTED_CASE_STATE)

        self.assertEqual(CaseLog.objects.count(), 1)
        outcome = CaseLog.objects.all()[0]

        self.assertEqual(outcome.logtype.code, self.VALID_OUTCOME_CODE)
        self.assertEqual(outcome.notes, 'lorem ipsum')

    def test_invalid_form(self):
        case = make_recipe('legalaid.case', state=CASE_STATES.OPEN)

        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(CaseLog.objects.count(), 0)

        form = self.FORM(case=case, data={
            'outcome_code': 'invalid',
            'outcome_notes': 'l'*501
        })

        self.assertFalse(form.is_valid())

        self.assertItemsEqual(
            form.errors, {
                'outcome_code': [u'Select a valid choice. That choice is not one of the available choices.'],
                'outcome_notes': [u'Ensure this value has at most 500 characters (it has 501).']
            }
        )

        # nothing has changed
        case = Case.objects.get(pk=case.pk)
        self.assertEqual(case.state, CASE_STATES.OPEN)

        self.assertEqual(CaseLog.objects.count(), 0)


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
