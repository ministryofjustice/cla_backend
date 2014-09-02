import datetime
import mock

from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from legalaid.models import Case
from legalaid.tests.views.mixins.case_api import FullCaseAPIMixin, \
    BaseSearchCaseAPIMixin, BaseUpdateCaseTestCase

from cla_common.constants import REQUIRES_ACTION_BY

from cla_eventlog.models import Log
from cla_eventlog.tests.test_views import ExplicitEventCodeViewTestCaseMixin, \
    ImplicitEventCodeViewTestCaseMixin

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe

from call_centre.forms import DeclineHelpCaseForm, \
    SuspendCaseForm
from call_centre.serializers import CaseSerializer


class BaseCaseTestCase(
    CLAOperatorAuthBaseApiTestMixin, FullCaseAPIMixin, APITestCase
):
    def get_case_serializer_clazz(self):
        return CaseSerializer

    @property
    def response_keys(self):
        return [
            'eligibility_check', 'personal_details', 'reference',
            'created', 'modified', 'created_by',
            'provider', 'notes', 'provider_notes',
            'full_name', 'laa_reference', 'eligibility_state',
            'adaptation_details', 'billable_time', 'requires_action_by',
            'matter_type1', 'matter_type2', 'diagnosis', 'media_code',
            'postcode', 'diagnosis_state', 'thirdparty_details', 'rejected',
            'date_of_birth', 'category',
            'exempt_user', 'exempt_user_reason', 'ecf_statement',
            'case_count'
        ]


class CaseGeneralTestCase(BaseCaseTestCase):
    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

        # ### DETAIL
        self._test_delete_not_allowed(self.detail_url)


class CreateCaseTestCase(BaseCaseTestCase):

    def test_create_doesnt_set_readonly_values_but_only_personal_details(self):
        """
            Only POST personal details allowed
        """
        pd = make_recipe('legalaid.personal_details')
        eligibility_check = make_recipe('legalaid.eligibility_check')
        thirdparty_details = make_recipe('legalaid.thirdparty_details')
        adaptation_details = make_recipe('legalaid.adaptation_details')
        diagnosis = make_recipe('diagnosis.diagnosis')
        provider = make_recipe('cla_provider.provider')
        media_code = make_recipe('legalaid.media_code')

        matter_type1 = make_recipe('legalaid.matter_type1')
        matter_type2 = make_recipe('legalaid.matter_type2')

        data = {
            'personal_details': unicode(pd.reference),
            'eligibility_check': unicode(eligibility_check.reference),
            'thirdparty_details': unicode(thirdparty_details.reference),
            'adaptation_details': unicode(adaptation_details.reference),
            'diagnosis': unicode(diagnosis.reference),
            'provider': unicode(provider.id),
            'notes': 'my notes',
            'billable_time': 234,
            'created': "2014-08-05T10:41:55.979Z",
            'modified': "2014-08-05T10:41:55.985Z",
            'created_by': "test_user",
            'matter_type1': matter_type1.code,
            'matter_type2': matter_type2.code,
            'media_code': media_code.code,
            'provider_notes': "bla",
            'laa_reference': 232323,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER_REVIEW
        }
        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

        self.assertCaseEqual(response.data,
            Case(
                reference=response.data['reference'],
                personal_details=pd,
                eligibility_check=None,
                thirdparty_details=None,
                adaptation_details=None,
                diagnosis=None,
                provider=None,
                notes=data['notes'],
                billable_time=0,
                laa_reference=response.data['laa_reference'],
                matter_type1=matter_type1,
                matter_type2=matter_type2,
                media_code=media_code,
                provider_notes=""
            )
        )

        self.assertNotEqual(response.data['requires_action_by'], data['requires_action_by'])
        self.assertNotEqual(response.data['created'], data['created'])
        self.assertNotEqual(response.data['created_by'], data['created_by'])
        self.assertNotEqual(response.data['modified'], data['modified'])
        self.assertNotEqual(response.data['laa_reference'], data['laa_reference'])

        self.assertLogInDB()

    def test_create_no_data(self):
        """
        CREATE should work, even with an empty POST
        """
        response = self.client.post(
            self.list_url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)
        self.assertEqual(response.data['eligibility_check'], None)

        # checking that requires_action_by is set to OPERATOR
        case = Case.objects.get(reference=response.data['reference'])
        self.assertEqual(case.requires_action_by, REQUIRES_ACTION_BY.OPERATOR)

        self.assertLogInDB()

    def test_create_with_data(self):
        media_code = make_recipe('legalaid.media_code')
        matter_type1 = make_recipe('legalaid.matter_type1')
        matter_type2 = make_recipe('legalaid.matter_type2')

        data = {
            'notes': 'my notes',
            'matter_type1': matter_type1.code,
            'matter_type2': matter_type2.code,
            'media_code': media_code.code,
            'provider_notes': "bla",
        }
        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertResponseKeys(response)

        self.assertCaseEqual(response.data,
            Case(
                reference=response.data['reference'],
                notes=data['notes'],
                matter_type1=matter_type1,
                matter_type2=matter_type2,
                media_code=media_code,
                provider_notes="",
                laa_reference=response.data['laa_reference'],
            )
        )

        self.assertLogInDB()

    def test_case_serializer_with_eligibility_check_reference(self):
        eligibility_check = make_recipe('legalaid.eligibility_check')

        data = {u'eligibility_check': eligibility_check.reference}
        serializer = CaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

    def test_case_serializer_with_personal_details_reference(self):
        personal_details = make_recipe('legalaid.personal_details', **{u'full_name': u'John Doe',
                                      u'home_phone': u'9876543210',
                                      u'mobile_phone': u'0123456789',
                                      u'postcode': u'SW1H 9AJ',
                                      u'street': u'102 Petty France',
                                      u'title': u'MR'})
        data = {u'personal_details': unicode(personal_details.reference)}

        serializer = CaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual( serializer.errors, {})

    def test_case_serializer_with_media_code(self):
        media_code = make_recipe('legalaid.media_code')

        data = {u'media_code': media_code.code}
        serializer = CaseSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})


class UpdateCaseTestCase(BaseUpdateCaseTestCase, BaseCaseTestCase):
    def test_patch_operator_notes_allowed(self):
        """
        Test that provider cannot post provider notes
        """
        response = self.client.patch(
            self.detail_url, data={'notes': 'abc123'},
            format='json', HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], 'abc123')

    def test_patch_provider_notes_not_allowed(self):
        """
        Test that provider cannot post provider notes
        """
        response = self.client.patch(
            self.detail_url, data={'provider_notes': 'abc123'},
            format='json', HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider_notes'], self.resource.provider_notes)
        self.assertNotEqual(response.data['provider_notes'], 'abc123')


class AssignCaseTestCase(BaseCaseTestCase):

    def test_assign_invalid_case_reference(self):
        url = reverse('call_centre:case-assign', args=(), kwargs={'reference': 'invalid'})

        response = self.client.post(
            url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, 404)

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_assign_case_without_category(self, tz_model_mock, tz_helper_tz):
        case = make_recipe('legalaid.case', eligibility_check=None)
        category = make_recipe('legalaid.category')
        return self._test_assign_successful(
            case, category, tz_model_mock, tz_helper_tz, is_manual=False
        )

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_manual_assign_successful(self, tz_model_mock, tz_helper_tz):
        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category
        return self._test_assign_successful(
            case, category, tz_model_mock, tz_helper_tz, is_manual=True
        )

    @mock.patch('cla_provider.models.timezone.now')
    @mock.patch('cla_provider.helpers.timezone.now')
    def test_automatic_assign_successful(self, tz_model_mock, tz_helper_tz):
        case = make_recipe('legalaid.case')
        category = case.eligibility_check.category
        return self._test_assign_successful(
            case, category, tz_model_mock, tz_helper_tz, is_manual=False
        )

    def _test_assign_successful(self,
            case, category, tz_model_mock, tz_helper_tz, is_manual=True
        ):
        fake_day = datetime.datetime(2014, 1, 2, 9, 1, 0).replace(tzinfo=timezone.get_current_timezone())
        tz_model_mock.return_value = fake_day
        tz_helper_tz.return_value = fake_day

        case.matter_type1 = make_recipe('legalaid.matter_type1', category=category)
        case.matter_type2 = make_recipe('legalaid.matter_type2', category=category)
        case.save()


        # preparing for test
        provider = make_recipe('cla_provider.provider', name='Provider Name', active=True)
        make_recipe('cla_provider.provider_allocation',
                                 weighted_distribution=0.5,
                                 provider=provider,
                                 category=category)

        # before being assigned, case is in the list
        case_list = self.client.get(
            self.list_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        ).data

        self.assertTrue(case.reference in [x.get('reference') for x in case_list['results']])

        # no outcome codes should exist at this point
        self.assertEqual(Log.objects.count(), 0)

        # assign
        url = reverse('call_centre:case-assign', args=(), kwargs={'reference': case.reference})

        data = {
            'suggested_provider': provider.pk,
            'provider_id': provider.pk,
            'is_manual': is_manual
        }
        if is_manual:
            data['notes'] = 'my notes'

        response = self.client.post(
            url, data=data,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        case = Case.objects.get(pk=case.pk)
        self.assertTrue(case.provider.pk != None)

        # after being assigned, it's gone from the dashboard...
        case_list = self.client.get(
            self.list_dashboard_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        ).data

        self.assertFalse(case.reference in [x.get('reference') for x in case_list['results']])

        # checking that requires_action_by is set to PROVIDER
        self.assertEqual(case.requires_action_by, REQUIRES_ACTION_BY.PROVIDER_REVIEW)

        # checking that the log object is there
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]
        self.assertEqual(log.case, case)
        self.assertEqual(log.notes, 'my notes' if is_manual else 'Assigned to Provider Name')
        self.assertEqual(log.created_by, self.user)

        # ... but the case still accessible from the full list
        case_list = self.client.get(
            self.list_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        ).data

        self.assertTrue(case.reference in [x.get('reference') for x in case_list['results']])

    def test_cannot_patch_provider_directly(self):
        """
        Need to use assign action instead
        """

        provider = make_recipe('cla_provider.provider', active=True)
        response = self.client.patch(self.detail_url, data={
            'provider': provider.pk
        }, format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider'], None)


class DeferAssignmentTestCase(ImplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'call_centre:case-defer-assignment', args=(),
            kwargs={'reference': reference}
        )


class DeclineHelpTestCase(ExplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_event_code(self):
        form = DeclineHelpCaseForm(case=mock.MagicMock())
        return form.fields['event_code'].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'call_centre:case-decline-help', args=(),
            kwargs={'reference': reference}
        )


class SuspendCaseTestCase(ExplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_event_code(self):
        form = SuspendCaseForm(case=mock.MagicMock())
        return form.fields['event_code'].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.resource.reference
        return reverse(
            'call_centre:case-suspend', args=(),
            kwargs={'reference': reference}
        )


class SearchCaseTestCase(BaseSearchCaseAPIMixin, BaseCaseTestCase):
    def test_list_with_dashboard_param(self):
        """
        Testing that if ?dashboard param is specified, it will exclude cases
        that are already assigned or don't requires_action_by == OPERATOR
        """
        Case.objects.all().delete()

        # obj1 is assigned should be excluded
        # obj2.requires_action_by == None (meaning doesn't require action)
        #   so should be excluded
        # obj3.requires_action_by == OPERATOR so should be included
        obj1 = make_recipe(
            'legalaid.case',
            reference='ref1', provider=self.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER
        )
        obj2 = make_recipe(
            'legalaid.case',
            reference='ref2', provider=None,
            requires_action_by=None
        )
        obj3 = make_recipe(
            'legalaid.case',
            reference='ref3', provider=None,
            requires_action_by=REQUIRES_ACTION_BY.OPERATOR
        )

        # searching via dashboard param => should return just obj3
        response = self.client.get(
            self.list_dashboard_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertCaseEqual(response.data['results'][0], obj3)

        # searching without dashboard param => should return all of them
        response = self.client.get(
            self.list_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(3, len(response.data['results']))
        self.assertItemsEqual(
            [case['reference'] for case in response.data['results']],
            ['ref1', 'ref2', 'ref3']
        )

    # person_ref PARAM

    def test_list_with_person_ref_param(self):
        """
        Testing that if ?person_ref param is specified, it will only return
        cases for that person
        """
        Case.objects.all().delete()

        pd1 = make_recipe('legalaid.personal_details')
        pd2 = make_recipe('legalaid.personal_details')

        obj1 = make_recipe(
            'legalaid.case', reference='ref1',
            personal_details=pd1
        )
        obj2 = make_recipe(
            'legalaid.case', reference='ref2',
            personal_details=pd2
        )
        obj3 = make_recipe(
            'legalaid.case', reference='ref3',
            personal_details=pd1
        )

        # searching for pd1
        response = self.client.get(
            self.get_list_person_ref_url(pd1.reference), format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data['results']))
        self.assertItemsEqual(
            [c['reference'] for c in response.data['results']],
            ['ref1', 'ref3']
        )

        # searching for pd2 AND dashboard=1 should ignore dashboard param
        url = '%s&dashboard=1' % self.get_list_person_ref_url(pd2.reference)
        response = self.client.get(
            url, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertItemsEqual(
            [case['reference'] for case in response.data['results']],
            ['ref2']
        )
