import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone
from legalaid.tests.views.mixins.resource import \
    NestedSimpleResourceCheckAPIMixin
import mock
from rest_framework import status
from rest_framework.test import APITestCase
from cla_eventlog.models import Log
from cla_eventlog.tests.test_views import ExplicitEventCodeViewTestCaseMixin, \
    ImplicitEventCodeViewTestCaseMixin
from legalaid.models import Case
from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe
from cla_common.constants import CASE_STATES
from call_centre.forms import DeclineAllSpecialistsCaseForm
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
             'created', 'modified', 'state', 'created_by',
             'provider', 'log_set', 'notes', 'provider_notes', 'in_scope',
             'full_name', 'laa_reference', 'eligibility_state', 'thirdparty_details',
             'adaptation_details']
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
        self.assertEqual(case.reference, data['reference'])
        if data['eligibility_check']:
            self.assertEqual(unicode(case.eligibility_check.reference), data['eligibility_check'])
        else:
            self.assertEqual(case.eligibility_check, None)
        self.assertPersonalDetailsEqual(data['personal_details'], case.personal_details)


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

    def test_create_with_data(self):
        check = make_recipe('legalaid.eligibility_check')
        pd = make_recipe('legalaid.personal_details', **{
                'title': 'MR',
                'full_name': 'John Doe',
                'postcode': 'SW1H 9AJ',
                'street': '102 Petty France',
                'mobile_phone': '0123456789',
                'home_phone': '9876543210',
            })
        data = {
            'eligibility_check': unicode(check.reference),
            'personal_details': unicode(pd.reference)
        }
        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        # check initial state is correct
        self.assertEqual(response.data['state'], CASE_STATES.OPEN)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

        self.assertCaseEqual(response.data,
            Case(
                reference=response.data['reference'],
                eligibility_check=check,
                personal_details=pd
            )
        )
        self.assertEqual(response.data['in_scope'], None)

    def test_create_with_data_in_scope(self):
        pd = make_recipe('legalaid.personal_details', **{
            'title': 'MR',
            'full_name': 'John Doe',
            'postcode': 'SW1H 9AJ',
            'street': '102 Petty France',
            'mobile_phone': '0123456789',
            'home_phone': '9876543210',
            })
        data = {
            'personal_details': unicode(pd.reference),
            'in_scope': True,
        }
        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        # check initial state is correct
        self.assertEqual(response.data['state'], CASE_STATES.OPEN)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

        self.assertCaseEqual(
            response.data,
            Case(
                reference=response.data['reference'],
                eligibility_check=None,
                personal_details=pd,
                in_scope=True
            )
        )

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

    def test_case_serializer_with_dupe_eligibility_check_reference(self):
        case = make_recipe('legalaid.case')
        personal_details = make_recipe('legalaid.personal_details', **{u'full_name': u'John Doe',
                                      u'home_phone': u'9876543210',
                                      u'mobile_phone': u'0123456789',
                                      u'postcode': u'SW1H 9AJ',
                                      u'street': u'102 Petty France',
                                      u'title': u'MR'})
        data = {u'eligibility_check': case.eligibility_check.reference,
                u'personal_details': unicode(personal_details.reference)}
        serializer = CaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertDictEqual(
            serializer.errors,
            {'eligibility_check':
                 [u'Case with this Eligibility check already exists.']})

    def test_cannot_create_with_other_eligibility_reference(self):
        """
        Cannot create a case passing an eligibility check reference already assigned
        to another case
        """
        # create a different case
        case = make_recipe('legalaid.case')
        pd = make_recipe('legalaid.personal_details', **{
                'title': 'MR',
                'full_name': 'John Doe',
                'postcode': 'SW1H 9AJ',
                'street': '102 Petty France',
                'mobile_phone': '0123456789',
                'home_phone': '9876543210',
            })

        data = {
            'eligibility_check': unicode(case.eligibility_check.reference),
            'personal_details':  unicode(pd.reference)
        }
        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'eligibility_check': [u'Case with this Eligibility check already exists.']}
        )


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

    def test_already_assigned(self):
        provider = make_recipe('cla_provider.provider', active=True)
        self.check.provider = provider
        self.check.save()

        response = self.client.post(
            self.url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {'__all__': [u'Case currently assigned to a provider']})


class DeclineAllSpecialistsTestCase(ExplicitEventCodeViewTestCaseMixin, BaseCaseTestCase):
    def get_event_code(self):
        form = DeclineAllSpecialistsCaseForm(case=mock.MagicMock())
        return form.fields['event_code'].choices[0][0]

    def get_url(self, reference=None):
        reference = reference or self.check.reference
        return reverse(
            'call_centre:case-decline-all-specialists', args=(),
            kwargs={'reference': reference}
        )


class SearchCaseTestCase(BaseCaseTestCase):

    def test_list_with_dashboard_param(self):
        """
        Testing that if ?dashboard param is specified, it will exclude cases
        that are already assigned or not open.
        """
        Case.objects.all().delete()

        # obj1 is assigned, obj2 is closed, obj3 is open and not assigned
        obj1 = make_recipe('legalaid.case',
              reference='ref1',
              provider=self.provider,
              state=CASE_STATES.OPEN
        )
        obj2 = make_recipe('legalaid.case',
              reference='ref2',
              provider=None,
              state=CASE_STATES.CLOSED
        )
        obj3 = make_recipe('legalaid.case',
              reference='ref3',
              provider=None,
              state=CASE_STATES.OPEN
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
            errors,
                expected_errors
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

        response = self._create(data=data)      # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCheckResponseKeys(response)
        self.assertAdaptationDetailsEqual(response.data, check)
