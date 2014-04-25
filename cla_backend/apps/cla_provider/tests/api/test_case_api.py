from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.timezone import utc

from rest_framework import status
from rest_framework.test import APITestCase

from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_ACCEPTED, \
    CASE_STATE_REJECTED

from core.tests.test_base import CLAProviderAuthBaseApiTestMixin, make_recipe

from legalaid.models import Case, CaseOutcome


class BaseCaseTests(CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(BaseCaseTests, self).setUp()

        self.list_url = reverse('cla_provider:case-list')
        obj = make_recipe('legalaid.tests.case', provider=self.provider)
        self.check = obj
        self.detail_url = reverse(
            'cla_provider:case-detail', args=(),
            kwargs={'reference': obj.reference}
        )

    def assertCaseCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['eligibility_check', 'personal_details', 'reference',
             'created', 'modified', 'state', 'created_by',
             'provider', 'locked_by', 'locked_at', 'notes', 'provider_notes']
        )

    def assertPersonalDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['title', 'full_name', 'postcode', 'street', 'town', 'mobile_phone', 'home_phone']:
                self.assertEqual(getattr(obj, prop), data[prop])

    def assertCaseEqual(self, data, case):
        self.assertEqual(case.reference, data['reference'])
        self.assertEqual(unicode(case.eligibility_check.reference), data['eligibility_check'])
        self.assertPersonalDetailsEqual(data['personal_details'], case.personal_details)


class CaseTests(BaseCaseTests):
    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

        ### DETAIL
        self._test_delete_not_allowed(self.detail_url)

        ### CREATE
        self._test_post_not_allowed(self.list_url)


    def test_methods_not_authorized_operator_key(self):
        """
        Ensure that we can't POST, PUT or DELETE using operator
        token
        """
        ### LIST
        self._test_delete_not_authorized(self.list_url, self.operator_token)

        ### DETAIL
        self._test_delete_not_authorized(self.detail_url, self.operator_token)

        ### CREATE
        self._test_post_not_authorized(self.list_url, self.operator_token)


    def test_list_allowed(self):
        """
        GET list-url should work
        """

        obj = make_recipe('legalaid.tests.case')
        obj.provider = self.provider
        obj.save()

        response = self.client.get(
            self.list_url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        self.assertCaseEqual(response.data[0], obj)
        self.assertCaseEqual(response.data[1], self.check)

    def test_get_allowed(self):
        response = self.client.get(
            self.detail_url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCaseCheckResponseKeys(response)
        self.assertCaseEqual(response.data, self.check)


    def test_locked_by_when_getting_case(self):

        self.assertEqual(self.check.locked_by, None)
        self.assertEqual(self.check.locked_at, None)
        response = self.client.get(
            self.detail_url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['locked_by'], 'john')

        # check the time was set by this test
        self.assertFalse(response.data['locked_at'] == None)
        time_diff = datetime.utcnow().replace(tzinfo=utc)-response.data['locked_at']
        self.assertTrue(time_diff.seconds<3)

    # SEARCH

    def test_search_find_one_result_by_name(self):
        """
        GET search by name should work
        """

        obj = make_recipe('legalaid.tests.case',
                          reference='ref1',
                          personal_details__full_name='xyz',
                          personal_details__postcode='123',
                          provider=self.provider,
                          )

        self.check.personal_details.full_name = 'abc'
        self.check.personal_details.postcode = '123'
        self.check.personal_details.save()
        self.check.reference = 'ref2'
        self.check.save()

        response = self.client.get(
            self.list_url, data={'search':'abc'}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertCaseEqual(response.data[0], self.check)

    def test_search_find_one_result_by_ref(self):
        """
        GET search by ref should work
        """

        obj = make_recipe('legalaid.tests.case', provider=self.provider,
                          personal_details__full_name='abc',
                          personal_details__postcode='123')


        response = self.client.get(
            self.list_url, data={'search':self.check.reference}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertCaseEqual(response.data[0], self.check)

    def test_search_find_one_result_by_postcode(self):
        """
        GET search by name should work
        """

        obj = make_recipe('legalaid.tests.case', provider=self.provider,
                          personal_details__postcode='123',
                          personal__details__full_name='abc')

        response = self.client.get(
            self.list_url, data={'search': self.check.personal_details.postcode},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
        self.assertCaseEqual(response.data[0], self.check)

    def test_search_find_none_result_by_postcode(self):
        """
        GET search by name should work
        """

        response = self.client.get(
            self.list_url, data={'search': self.check.personal_details.postcode+'ss'},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))


    def test_search_find_none_result_by_fullname(self):
        """
        GET search by name should work
        """
        response = self.client.get(
            self.list_url, data={'search': self.check.personal_details.full_name+'ss'},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))


    def test_search_find_none_result_by_ref(self):
        """
        GET search by name should work
        """
        response = self.client.get(
            self.list_url, data={'search': self.check.reference+'ss'},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))

    def test_patch_provider_notes_allowed(self):
        """
        Test that provider can post provider notes
        """
        response = self.client.patch(self.detail_url, data={'provider_notes': 'abc123'},
                                     format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider_notes'], 'abc123')



class StateChangeMixin(object):
    def setUp(self):
        super(StateChangeMixin, self).setUp()

        self.outcome_codes = [
            make_recipe('legalaid.tests.outcome_code', code="CODE_OPEN", case_state=CASE_STATE_OPEN),
            make_recipe('legalaid.tests.outcome_code', code="CODE_ACCEPTED", case_state=CASE_STATE_ACCEPTED),
            make_recipe('legalaid.tests.outcome_code', code="CODE_REJECTED", case_state=CASE_STATE_REJECTED),
        ]
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


class RejectCaseTests(StateChangeMixin, BaseCaseTests):
    def get_state_change_url(self, reference=None):
        reference = reference or self.check.reference
        return reverse(
            'cla_provider:case-reject', args=(),
            kwargs={'reference': reference}
        )

    def test_successful(self):
        # before, case open and no outcomes
        self.assertEqual(self.check.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)

        # reject
        data={
                'outcome_code': 'CODE_REJECTED',
                'outcome_notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # after, case rejected and outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, CASE_STATE_REJECTED)

        self.assertEqual(CaseOutcome.objects.count(), 1)
        outcome = CaseOutcome.objects.all()[0]

        self.assertEqual(outcome.case, self.check)
        self.assertEqual(outcome.outcome_code.code, data['outcome_code'])
        self.assertEqual(outcome.notes, data['outcome_notes'])

    def test_invalid_mutation(self):
        # before, case accepted and no outcomes
        self.check.state = CASE_STATE_ACCEPTED
        self.check.save()
        self.assertEqual(self.check.state, CASE_STATE_ACCEPTED)

        self.assertEqual(CaseOutcome.objects.count(), 0)

        # reject
        data={
                'outcome_code': 'CODE_REJECTED',
                'outcome_notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'case_state': [u"Case should be 'OPEN' to be rejected but it's currently 'ACCEPTED'"]}
        )

        # after, case didn't change and no outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, CASE_STATE_ACCEPTED)

        self.assertEqual(CaseOutcome.objects.count(), 0)

    def test_invalid_outcome_code(self):
        # before, case open and no outcomes
        self.assertEqual(self.check.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)

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
        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)


class AcceptCaseTests(StateChangeMixin, BaseCaseTests):
    def get_state_change_url(self, reference=None):
        reference = reference or self.check.reference
        return reverse(
            'cla_provider:case-accept', args=(),
            kwargs={'reference': reference}
        )

    def test_successful(self):
        # before, case open and no outcomes
        self.assertEqual(self.check.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)

        # reject
        data={
                'outcome_code': 'CODE_ACCEPTED',
                'outcome_notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # after, case rejected and outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, CASE_STATE_ACCEPTED)

        self.assertEqual(CaseOutcome.objects.count(), 1)
        outcome = CaseOutcome.objects.all()[0]

        self.assertEqual(outcome.case, self.check)
        self.assertEqual(outcome.outcome_code.code, data['outcome_code'])
        self.assertEqual(outcome.notes, data['outcome_notes'])

    def test_invalid_mutation(self):
        # before, case accepted and no outcomes
        self.check.state = CASE_STATE_ACCEPTED
        self.check.save()
        self.assertEqual(self.check.state, CASE_STATE_ACCEPTED)

        self.assertEqual(CaseOutcome.objects.count(), 0)

        # reject
        data={
                'outcome_code': 'CODE_ACCEPTED',
                'outcome_notes': 'lorem ipsum'
            }
        response = self.client.post(
            self.state_change_url, data=data,
            format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'case_state': [u"Case should be 'OPEN' to be accepted but it's currently 'ACCEPTED'"]}
        )

        # after, case didn't change and no outcome created
        case = Case.objects.get(pk=self.check.pk)
        self.assertEqual(case.state, CASE_STATE_ACCEPTED)

        self.assertEqual(CaseOutcome.objects.count(), 0)

    def test_invalid_outcome_code(self):
        # before, case open and no outcomes
        self.assertEqual(self.check.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)

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
        self.assertEqual(case.state, CASE_STATE_OPEN)

        self.assertEqual(CaseOutcome.objects.count(), 0)
