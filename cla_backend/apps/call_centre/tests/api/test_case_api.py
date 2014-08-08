import datetime
import mock

from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from legalaid.tests.views.mixins.resource import \
    NestedSimpleResourceCheckAPIMixin
from legalaid.models import Case
from cla_common.constants import REQUIRES_ACTION_BY

from cla_eventlog.models import Log
from cla_eventlog.tests.test_views import ExplicitEventCodeViewTestCaseMixin, \
    ImplicitEventCodeViewTestCaseMixin

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe

from call_centre.forms import DeclineHelpCaseForm, \
    SuspendCaseForm
from call_centre.serializers import CaseSerializer


class BaseCaseTestCase(CLAOperatorAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(BaseCaseTestCase, self).setUp()

        self.list_url = reverse('call_centre:case-list')
        self.list_dashboard_url = u'%s?dashboard=1' % reverse('call_centre:case-list')
        self.case_obj = make_recipe('legalaid.case')
        self.check = self.case_obj
        self.detail_url = reverse(
            'call_centre:case-detail', args=(),
            kwargs={'reference': self.case_obj.reference}
        )

    def assertCaseResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['eligibility_check', 'personal_details', 'reference',
             'created', 'modified', 'created_by',
             'provider', 'log_set', 'notes', 'provider_notes',
             'full_name', 'laa_reference', 'eligibility_state', 'thirdparty_details',
             'adaptation_details', 'billable_time', 'requires_action_by',
             'matter_type1', 'matter_type2', 'diagnosis', 'media_code',
             'postcode', 'diagnosis_state', 'rejected']
        )

    def assertPersonalDetailsEqual(self, data, obj):
        if isinstance(data, basestring):
            self.assertEqual(unicode(data), unicode(obj.reference))
            return
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['title', 'full_name', 'postcode', 'street', 'mobile_phone', 'home_phone']:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])

    def assertCaseEqual(self, data, case):
        """
            'provider': unicode(provider.id),
            'laa_reference': 3000314,
            'matter_type1': matter_type1.code,
            'matter_type2': matter_type2.code,
            'media_code': media_code.code,
            'provider_notes': "bla",
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER_REVIEW
        """

        self.assertEqual(case.reference, data['reference'])

        fks = {
            'eligibility_check': 'reference', 
            'personal_details': 'reference', 
            'thirdparty_details': 'reference',
            'adaptation_details': 'reference',
            'diagnosis': 'reference',
            'matter_type1': 'code',
            'matter_type2': 'code',
            'media_code': 'code',
        }

        for field, fk_pk in fks.items():
            if not field in data: continue

            val = getattr(case, field)
            if val:
                val = unicode(getattr(val, fk_pk))
            self.assertEqual(val, data[field])

        for field in [
            'notes', 'billable_time', 'laa_reference', 
            'provider_notes', 'requires_action_by'

        ]:
            if not field in data: continue

            self.assertEqual(getattr(case, field), data[field], '%s: %s - %s' % (
                field, getattr(case, field), data[field])
            )
        
        self.assertPersonalDetailsEqual(data['personal_details'], case.personal_details)

    def assertLogInDB(self):
        self.assertEqual(Log.objects.count(), 1)

    def assertNoLogInDB(self):
        self.assertEqual(Log.objects.count(), 0)


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

    def test_create_doesnt_set_readonly_values(self):
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
        self.assertCaseResponseKeys(response)

        self.assertCaseEqual(response.data,
            Case(
                reference=response.data['reference'],
                personal_details=None,
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
        self.assertCaseResponseKeys(response)
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
        self.assertCaseResponseKeys(response)

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
        reference = reference or self.check.reference
        return reverse(
            'call_centre:case-defer-assignment', args=(),
            kwargs={'reference': reference}
        )


class DeclineHelpTestCase(ExplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_event_code(self):
        form = DeclineHelpCaseForm(case=mock.MagicMock())
        return form.fields['event_code'].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.check.reference
        return reverse(
            'call_centre:case-decline-help', args=(),
            kwargs={'reference': reference}
        )


class SuspendCaseTestCase(ExplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_event_code(self):
        form = SuspendCaseForm(case=mock.MagicMock())
        return form.fields['event_code'].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.check.reference
        return reverse(
            'call_centre:case-suspend', args=(),
            kwargs={'reference': reference}
        )


class SearchCaseTestCase(BaseCaseTestCase):

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

    def test_search_find_one_result_by_name(self):
        """
        GET search by name should work
        """

        obj = make_recipe('legalaid.case',
              reference='ref1',
              personal_details__full_name='xyz',
              personal_details__postcode='123',
              provider=self.provider,
        )

        self.case_obj.personal_details.full_name = 'abc'
        self.case_obj.personal_details.postcode = '123'
        self.case_obj.personal_details.save()
        self.case_obj.reference = 'ref2'
        self.case_obj.save()

        response = self.client.get(
            self.list_url, data={'search':'abc'}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertCaseEqual(response.data['results'][0], self.case_obj)

    def test_search_find_one_result_by_ref(self):
        """
        GET search by name should work
        """

        obj = make_recipe('legalaid.case', provider=self.provider,
                          personal_details__full_name='abc',
                          personal_details__postcode='123')

        response = self.client.get(
            self.list_url, data={'search':self.case_obj.reference}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertCaseEqual(response.data['results'][0], self.case_obj)

    def test_search_find_one_result_by_postcode(self):
        """
        GET search by name should work
        """

        obj = make_recipe('legalaid.case', provider=self.provider,
                          personal_details__postcode='123',
                          personal__details__full_name='abc')

        response = self.client.get(
            self.list_url, data={'search': self.case_obj.personal_details.postcode},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertCaseEqual(response.data['results'][0], self.case_obj)

    def test_search_find_none_result_by_postcode(self):
        """
        GET search by name should work
        """

        response = self.client.get(
            self.list_url, data={'search': self.case_obj.personal_details.postcode+'ss'},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data['results']))

    def test_search_find_none_result_by_fullname(self):
        """
        GET search by name should work
        """
        response = self.client.get(
            self.list_url, data={'search': self.case_obj.personal_details.full_name+'ss'},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data['results']))

    def test_search_find_none_result_by_ref(self):
        """
        GET search by name should work
        """
        response = self.client.get(
            self.list_url, data={'search': self.case_obj.reference+'ss'},
            format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data['results']))

    def test_patch_provider_notes_not_allowed(self):
        """
        Test that provider can post provider notes
        """
        response = self.client.patch(self.detail_url, data={'provider_notes': 'abc123'},
                                     format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['provider_notes'], self.case_obj.provider_notes)
        self.assertNotEqual(response.data['provider_notes'], 'abc123')


class AdaptationDetailsTestCase(CLAOperatorAuthBaseApiTestMixin, NestedSimpleResourceCheckAPIMixin, APITestCase):

    API_URL_NAMESPACE = 'call_centre'
    BASE_NAME = 'adaptationdetails'
    CHECK_RECIPE = 'legalaid.adaptation_details'

    @property
    def check_keys(self):
        return \
        [ 'reference',
          'bsl_webcam',
          'minicom',
          'text_relay',
          'skype_webcam',
          'callback_preference',
          'language',
          'notes'
        ]

    def get_http_authorization(self):
        return 'Bearer %s' % self.token

    def _get_default_post_data(self):
        return {'bsl_webcam' : True,
                'minicom' : True,
                'text_relay' : True,
                'skype_webcam' : True,
                'callback_preference' : True,
                'language' : 'WELSH',
                'notes' : 'abc'
                }

    def _test_method_in_error(self, method, url):

        # most fields are optional and variable type is just evaluated
        # by python rules to a boolean. i.e. passing strings etc. instead
        # of a JS boolean will still be evaluated to True in python.
        data={ 'language' : 'KLINGON' }


        method_callable = getattr(self.client, method)
        response = method_callable(url, data,
                                   format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_errors = {
            'language' : [u'Select a valid choice. XXXXXXXXX is not one of the available choices.'],
            }

        self.maxDiff = None
        errors = response.data
        self.assertItemsEqual(
            errors.keys(), expected_errors.keys()
        )
        self.assertItemsEqual(
            errors, expected_errors
        )

    def assertAdaptationDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['bsl_webcam', 'minicom', 'text_relay', 'skype_webcam',
                         'language','notes', 'callback_preference']:
                #self.assertEqual(unicode(getattr(obj, prop)), data[prop])
                self.assertEqual(obj[prop], data[prop])

    def test_methods_not_allowed(self):
        """
        Ensure that we can't DELETE to list url
        """
        ### LIST
        if hasattr(self, 'list_url') and self.list_url:
            self._test_delete_not_allowed(self.list_url)

    def test_methods_in_error(self):
        self._test_method_in_error('patch', self.detail_url)
        self._test_method_in_error('put', self.detail_url)

    # CREATE
    def test_create_with_data(self):
        """
        check variables sent as same as those that return.
        """
        data = self._get_default_post_data()
        check = self._get_default_post_data()

        response = self._create(data=data)  # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCheckResponseKeys(response)
        self.assertAdaptationDetailsEqual(response.data, check)
