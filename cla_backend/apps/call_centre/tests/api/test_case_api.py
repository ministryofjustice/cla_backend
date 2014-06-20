import datetime
import uuid

from django.core.urlresolvers import reverse
from django.utils import timezone
import mock

from rest_framework import status
from rest_framework.test import APITestCase

from legalaid.models import EligibilityCheck, \
    Case, CaseLog, CaseLogType
from legalaid.tests.base import StateChangeAPIMixin

from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from core.tests.mommy_utils import make_recipe
from cla_common.constants import CASE_STATES

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

    def assertCaseCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['eligibility_check', 'personal_details', 'reference',
             'created', 'modified', 'state', 'created_by',
             'provider', 'caseoutcome_set', 'notes', 'provider_notes', 'in_scope',
             'full_name', 'thirdparty_details', 'adaptation_details']
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
        self.assertEqual(unicode(case.eligibility_check.reference), data['eligibility_check'])
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
        self.assertCaseCheckResponseKeys(response)

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
        self.assertCaseCheckResponseKeys(response)

        self.assertCaseEqual(response.data,
            Case(
                reference=response.data['reference'],
                eligibility_check=check,
                personal_details=pd
            )
        )
        self.assertEqual(response.data['in_scope'], None)

    def test_create_with_data_in_scope(self):
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
        self.assertCaseCheckResponseKeys(response)

        self.assertCaseEqual(response.data,
                             Case(
                                 reference=response.data['reference'],
                                 eligibility_check=check,
                                 personal_details=pd,
                                 in_scope=True
                             )
        )

    def test_create_with_data_out_scope(self):
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
            'personal_details': unicode(pd.reference),
            'in_scope': False,
            }
        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        # check initial state is correct
        self.assertEqual(response.data['state'], CASE_STATES.OPEN)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseCheckResponseKeys(response)

        self.assertCaseEqual(response.data,
                             Case(
                                 reference=response.data['reference'],
                                 eligibility_check=check,
                                 personal_details=pd,
                                 in_scope=False
                             )
        )

    def test_create_without_eligibility_check(self):
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
        }
        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        # check initial state is correct
        self.assertEqual(response.data['state'], CASE_STATES.OPEN)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseCheckResponseKeys(response)

        self.assertCaseEqual(response.data,
                             Case(
                                 reference=response.data['reference'],
                                 eligibility_check=EligibilityCheck.objects.get(reference=response.data['eligibility_check']),
                                 personal_details=pd
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
    def test_assign_successful(self, tz_model_mock, tz_helper_tz):

        fake_day = datetime.datetime(2014, 1, 2, 9, 1, 0).replace(tzinfo=timezone.get_current_timezone())
        tz_model_mock.return_value = fake_day
        tz_helper_tz.return_value = fake_day

        case = make_recipe('legalaid.case')

        category = case.eligibility_check.category
        make_recipe('legalaid.refsp_logtype')
        make_recipe('legalaid.manalc_logtype')
        provider = make_recipe('cla_provider.provider', active=True)
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

        # no manual allocation outcome codes should exist at this point
        clt = CaseLogType.objects.get(code='MANALC')
        manual_alloc_records_count = CaseLog.objects.filter(logtype=clt).count()
        self.assertEqual(manual_alloc_records_count, 0)

        # assign

        url = reverse('call_centre:case-assign', args=(), kwargs={'reference': case.reference})

        data = {'suggested_provider': provider.pk, 'provider_id': provider.pk, 'is_manual': True}
        response = self.client.post(
            url, data=data,
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        case = Case.objects.get(pk=case.pk)
        self.assertTrue(case.provider.pk!=None)

        # after being assigned, it's gone from the dashboard...
        case_list = self.client.get(
            self.list_dashboard_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        ).data

        self.assertFalse(case.reference in [x.get('reference') for x in case_list['results']])

        manual_alloc_records_count = CaseLog.objects.filter(logtype=clt).count()
        self.assertEqual(manual_alloc_records_count, 1)

        # ... but still accessible from the list
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


class CloseCaseTestCase(BaseCaseTestCase):

    def test_close_invalid_case_reference(self):
        url = reverse('call_centre:case-close', args=(), kwargs={'reference': 'invalid'})

        response = self.client.post(
            url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, 404)

    def test_close_successful(self):
        case = make_recipe('legalaid.case')

        # before being closed, case in the list
        case_list = self.client.get(
            self.list_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        ).data

        self.assertTrue(case.reference in [x.get('reference') for x in case_list['results']])

        # close

        url = reverse('call_centre:case-close', args=(), kwargs={'reference': case.reference})

        response = self.client.post(
            url, data={},
            HTTP_AUTHORIZATION='Bearer %s' % self.token,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        case = Case.objects.get(pk=case.pk)

        # after being closed, it's gone from the dashboard...
        case_list = self.client.get(
            self.list_dashboard_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        ).data

        self.assertFalse(case.reference in [x.get('reference') for x in case_list['results']])

        # ...but still accessible from the list
        case_list = self.client.get(
            self.list_url, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        ).data

        self.assertTrue(case.reference in [x.get('reference') for x in case_list['results']])


    def test_cannot_patch_state_directly(self):
        """
        Need to use close action instead
        """

        self.assertEqual(self.case_obj.state, CASE_STATES.OPEN)

        response = self.client.patch(self.detail_url, data={
            'state': CASE_STATES.CLOSED
        }, format='json', HTTP_AUTHORIZATION='Bearer %s' % self.token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], CASE_STATES.OPEN)


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


class DeclineAllSpecialistsTestCase(StateChangeAPIMixin, BaseCaseTestCase):
    VALID_OUTCOME_CODE = 'CODE_DECLINED_ALL_SPECIALISTS'
    EXPECTED_CASE_STATE = CASE_STATES.CLOSED

    def get_state_change_url(self, reference=None):
        reference = reference or self.check.reference
        return reverse(
            'call_centre:case-decline-all-specialists', args=(),
            kwargs={'reference': reference}
        )

    def test_invalid_mutation(self):
        """
            Overriding as not possible to test
        """
        pass


class PersonalDetailsTestCase(CLAOperatorAuthBaseApiTestMixin, APITestCase):

    def assertPersonalDetailsCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            [
                'reference',
                'title',
                'full_name',
                'postcode',
                'street',
                'mobile_phone',
                'home_phone'
            ]
        )

    def setUp(self):
        super(PersonalDetailsTestCase, self).setUp()

        self.list_url = reverse('call_centre:personaldetails-list')
        self.personal_details_obj = make_recipe('legalaid.personal_details')
        self.check = self.personal_details_obj
        self.detail_url = reverse(
            'call_centre:personaldetails-detail', args=(),
            kwargs={'reference': unicode(self.personal_details_obj.reference)}
        )

    def _get_default_post_data(self):
        return {
            'title': 'MR',
            'full_name': 'John Doe',
            'postcode': 'SW1H 9AJ',
            'street': '102 Petty France',
            'mobile_phone': '0123456789',
            'home_phone': '9876543210',
            }

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        data={
            "title": '1'*21,
            "full_name": '1'*456,
            "postcode": '1'*13,
            "street": '1'*256,
            "mobile_phone": '1'*21,
            "home_phone": '1'*21,
            }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data,
                                   format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_errors = {
            'title': [u'Ensure this value has at most 20 characters (it has 21).'],
            'full_name': [u'Ensure this value has at most 400 characters (it has 456).'],
            'postcode': [u'Ensure this value has at most 12 characters (it has 13).'],
            'street': [u'Ensure this value has at most 255 characters (it has 256).'],
            'mobile_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
            'home_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
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

    def assertPersonalDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['title', 'full_name', 'postcode', 'street', 'mobile_phone', 'home_phone']:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

    def test_methods_in_error(self):
        self._test_method_in_error('post', self.list_url)
        self._test_method_in_error('patch', self.detail_url)
        self._test_method_in_error('put', self.detail_url)

    # CREATE

    def test_create_no_data(self):
        """
        CREATE should work, even with an empty POST
        """
        response = self.client.post(
            self.list_url, data={}, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertPersonalDetailsCheckResponseKeys(response)

    def test_create_with_data(self):
        data = self._get_default_post_data()
        check = make_recipe('legalaid.personal_details', **data)

        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertPersonalDetailsCheckResponseKeys(response)

        self.assertPersonalDetailsEqual(response.data, check)

class ThirdPartyDetailsTestCase(CLAOperatorAuthBaseApiTestMixin, APITestCase):

    def assertThirdPartyDetailsCheckResponseKeys(self, response):

        self.assertItemsEqual(
            response.data.keys(),
            [
                'reference',
                'personal_details',
                'pass_phrase',
                'reason',
                'personal_relationship'
            ]
        )

    def setUp(self):
        super(ThirdPartyDetailsTestCase, self).setUp()

        self.list_url = reverse('call_centre:thirdpartydetails-list')
        self.personal_details_obj = make_recipe('legalaid.thirdparty_details')
        self.check = self.personal_details_obj
        self.detail_url = reverse(
            'call_centre:thirdpartydetails-detail', args=(),
            kwargs={'reference': unicode(self.personal_details_obj.reference)}
        )

    def _get_default_post_data(self):
        return {"personal_details": {
                    "title": "Mr",
                    "full_name": "Bob",
                    "postcode": "SW1H 9AJ",
                    "street": "102 Petty France",
                    "mobile_phone": "07000000000",
                    "home_phone": "01179000000",
                    },
                "pass_phrase": "monkey",
                "reason": "CHILD_PATIENT",
                "personal_relationship": "OTHER"
                }


    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        data={"personal_details": {
                    "title": '1'*21,
                    "full_name": '1'*456,
                    "postcode": '1'*13,
                    "street": '1'*256,
                    "mobile_phone": '1'*21,
                    "home_phone": '1'*21,
                },
                "pass_phrase": 'XXXXXXXXX',
                "reason": "XXXXXXXXX",
                "personal_relationship": "XXXXXXXXX"
                }


        method_callable = getattr(self.client, method)
        response = method_callable(url, data,
                                   format='json',
                                   HTTP_AUTHORIZATION='Bearer %s' % self.token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_errors = {
            'personal_details' : [{'full_name': [u'Ensure this value has at most 400 characters (it has 456).'],
                                   'home_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
                                   'mobile_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
                                   'postcode': [u'Ensure this value has at most 12 characters (it has 13).'],
                                   'street': [u'Ensure this value has at most 255 characters (it has 256).'],
                                   'title': [u'Ensure this value has at most 20 characters (it has 21).']
                                }],
            'reason': [u'Select a valid choice. XXXXXXXXX is not one of the available choices.'],
            'personal_relationship': [u'Select a valid choice. XXXXXXXXX is not one of the available choices.'],
            }

#         self.maxDiff = None
        errors = response.data
        self.assertItemsEqual(
            errors.keys(), expected_errors.keys()
        )
        self.assertItemsEqual(
            errors,
                expected_errors
        )

    def assertThirdPartyDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['pass_phrase','reason','personal_relationship']:
                #self.assertEqual(unicode(getattr(obj, prop)), data[prop])
                self.assertEqual(obj[prop], data[prop])

    def test_methods_not_allowed(self):
        """
        Ensure that we can't DELETE to list url
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

    def test_methods_in_error(self):
        self._test_method_in_error('post', self.list_url)
        self._test_method_in_error('patch', self.detail_url)
        self._test_method_in_error('put', self.detail_url)

    # CREATE
    def test_create_with_data(self):
        """
        check variables sent as same as those that return.
        """
        data = self._get_default_post_data()
        check = self._get_default_post_data()

        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertThirdPartyDetailsCheckResponseKeys(response)

        self.assertThirdPartyDetailsEqual(response.data, check)

class AdaptationDetailsTestCase(CLAOperatorAuthBaseApiTestMixin, APITestCase):

    def assertAdaptationDetailsCheckResponseKeys(self, response):

        self.assertItemsEqual(
            response.data.keys(),
            [ 'reference',
              'bsl_webcam',
              'minicom',
              'text_relay',
              'skype_webcam',
              'language',
              'notes'
            ]
        )

    def setUp(self):
        super(AdaptationDetailsTestCase, self).setUp()

        self.list_url = reverse('call_centre:adaptationdetails-list')
        self.personal_details_obj = make_recipe('legalaid.adaptation_details')
        self.check = self.personal_details_obj
        self.detail_url = reverse(
            'call_centre:adaptationdetails-detail', args=(),
            kwargs={'reference': unicode(self.personal_details_obj.reference)}
        )

    def _get_default_post_data(self):
        return {'bsl_webcam' : True,
                'minicom' : True,
                'text_relay' : True,
                'skype_webcam' : True,
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
                         'language','notes']:
                #self.assertEqual(unicode(getattr(obj, prop)), data[prop])
                self.assertEqual(obj[prop], data[prop])

    def test_methods_not_allowed(self):
        """
        Ensure that we can't DELETE to list url
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

    def test_methods_in_error(self):
        self._test_method_in_error('post', self.list_url)
        self._test_method_in_error('patch', self.detail_url)
        self._test_method_in_error('put', self.detail_url)

    # CREATE
    def test_create_with_data(self):
        """
        check variables sent as same as those that return.
        """
        data = self._get_default_post_data()
        check = self._get_default_post_data()

        response = self.client.post(
            self.list_url, data=data, format='json',
            HTTP_AUTHORIZATION='Bearer %s' % self.token
        )
        # check initial state is correct

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAdaptationDetailsCheckResponseKeys(response)
        self.assertAdaptationDetailsEqual(response.data, check)
