from django.core.urlresolvers import reverse

from rest_framework import status

from cla_common.constants import REQUIRES_ACTION_BY

from core.tests.mommy_utils import make_recipe

from legalaid.models import Case

from cla_eventlog.models import Log


class FullCaseAPIMixin(object):
    API_URL_NAMESPACE = None

    def setUp(self):
        super(FullCaseAPIMixin, self).setUp()

        self.list_url = reverse('%s:case-list' % self.API_URL_NAMESPACE)
        self.list_dashboard_url = u'%s?dashboard=1' % reverse(
            '%s:case-list' % self.API_URL_NAMESPACE
        )
        self.case_obj = make_recipe('legalaid.case')
        self.check = self.case_obj
        self.detail_url = self.get_details_url(self.case_obj)

    def get_http_authorization(self):
        raise NotImplementedError()

    def get_case_serializer_clazz(self):
        raise NotImplementedError()

    def get_details_url(self, case):
        return reverse(
            '%s:case-detail' % self.API_URL_NAMESPACE, args=(),
            kwargs={'reference': case.reference}
        )

    def get_extra_search_make_recipe_kwargs(self):
        return {}

    def assertCaseResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(), [
                'eligibility_check', 'personal_details', 'reference',
                'created', 'modified', 'created_by',
                'provider', 'log_set', 'notes', 'provider_notes',
                'full_name', 'laa_reference', 'eligibility_state',
                'adaptation_details', 'billable_time', 'requires_action_by',
                'matter_type1', 'matter_type2', 'diagnosis', 'media_code',
                'postcode', 'diagnosis_state', 'thirdparty_details',
                'exempt_user', 'exempt_user_reason', 'ecf_statement',
            ]
        )

    def assertPersonalDetailsEqual(self, data, obj):
        if isinstance(data, basestring):
            self.assertEqual(unicode(data), unicode(obj.reference))
            return
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in [
                'title', 'full_name', 'postcode', 'street',
                'mobile_phone', 'home_phone'
            ]:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])

    def assertCaseEqual(self, data, case):
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
            if not field in data:
                continue

            val = getattr(case, field)
            if val:
                val = unicode(getattr(val, fk_pk))
            self.assertEqual(
                val, data[field],
                '%s: %s - %s' % (field, val, data[field])
            )

        for field in [
            'notes', 'billable_time', 'laa_reference',
            'provider_notes', 'requires_action_by', 'exempt_user', 'exempt_user_reason'

        ]:
            if not field in data:
                continue

            self.assertEqual(getattr(case, field), data[field], '%s: %s - %s' % (
                field, getattr(case, field), data[field])
            )

        self.assertPersonalDetailsEqual(
            data['personal_details'], case.personal_details
        )

    def assertLogInDB(self):
        self.assertEqual(Log.objects.count(), 1)

    def assertNoLogInDB(self):
        self.assertEqual(Log.objects.count(), 0)

    def test_case_serializer_with_eligibility_check_reference(self):
        eligibility_check = make_recipe('legalaid.eligibility_check')

        data = {u'eligibility_check': eligibility_check.reference}
        serializer = self.get_case_serializer_clazz()(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

    def test_case_serializer_with_personal_details_reference(self):
        personal_details = make_recipe(
            'legalaid.personal_details',
            **{u'full_name': u'John Doe',
                u'home_phone': u'9876543210',
                u'mobile_phone': u'0123456789',
                u'postcode': u'SW1H 9AJ',
                u'street': u'102 Petty France',
                u'title': u'MR'
            }
        )
        data = {u'personal_details': unicode(personal_details.reference)}

        serializer = self.get_case_serializer_clazz()(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})

    def test_case_serializer_with_media_code(self):
        media_code = make_recipe('legalaid.media_code')

        data = {u'media_code': media_code.code}
        serializer = self.get_case_serializer_clazz()(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {})


class BaseSearchCaseAPIMixin(FullCaseAPIMixin):
    def test_search_find_one_result_by_name(self):
        """
        GET search by name should work
        """

        obj = make_recipe(
            'legalaid.case',
            reference='ref1',
            personal_details__full_name='xyz',
            personal_details__postcode='123',
            **self.get_extra_search_make_recipe_kwargs()
        )

        self.case_obj.personal_details.full_name = 'abc'
        self.case_obj.personal_details.postcode = '123'
        self.case_obj.personal_details.save()
        self.case_obj.reference = 'ref2'
        self.case_obj.save()

        response = self.client.get(
            self.list_url, data={'search': 'abc'}, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertCaseEqual(response.data['results'][0], self.case_obj)

    def test_search_find_one_result_by_ref(self):
        """
        GET search by name should work
        """

        obj = make_recipe(
            'legalaid.case',
            personal_details__full_name='abc',
            personal_details__postcode='123',
            **self.get_extra_search_make_recipe_kwargs()
        )

        response = self.client.get(
            self.list_url, data={'search':self.case_obj.reference}, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data['results']))
        self.assertCaseEqual(response.data['results'][0], self.case_obj)

    def test_search_find_one_result_by_postcode(self):
        """
        GET search by name should work
        """

        obj = make_recipe(
            'legalaid.case',
            personal_details__postcode='123',
            personal__details__full_name='abc',
            **self.get_extra_search_make_recipe_kwargs()
        )

        response = self.client.get(
            self.list_url, data={'search': self.case_obj.personal_details.postcode},
            format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
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
            HTTP_AUTHORIZATION=self.get_http_authorization()
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
            HTTP_AUTHORIZATION=self.get_http_authorization()
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
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data['results']))


class BaseUpdateCaseTestCase(FullCaseAPIMixin):

    def test_update_doesnt_set_readonly_values(self):
        case = make_recipe(
            'legalaid.case',
            eligibility_check=None,
            personal_details=None,
            thirdparty_details=None,
            adaptation_details=None,
            diagnosis=None,
            media_code=None,
            matter_type1=None,
            matter_type2=None,
            **self.get_extra_search_make_recipe_kwargs()
        )
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
            'billable_time': 234,
            'created': "2014-08-05T10:41:55.979Z",
            'modified': "2014-08-05T10:41:55.985Z",
            'created_by': "test_user",
            'matter_type1': matter_type1.code,
            'matter_type2': matter_type2.code,
            'media_code': media_code.code,
            'laa_reference': 232323,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER_REVIEW
        }
        response = self.client.patch(
            self.get_details_url(case), data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
                billable_time=0,
                laa_reference=response.data['laa_reference'],
                matter_type1=matter_type1,
                matter_type2=matter_type2,
                media_code=media_code,
                requires_action_by=case.requires_action_by
            )
        )

        self.assertNotEqual(response.data['requires_action_by'], data['requires_action_by'])
        self.assertNotEqual(response.data['created'], data['created'])
        self.assertNotEqual(response.data['created_by'], data['created_by'])
        self.assertNotEqual(response.data['modified'], data['modified'])
        self.assertNotEqual(response.data['laa_reference'], data['laa_reference'])

        self.assertNoLogInDB()

    def test_update_with_data(self):
        media_code = make_recipe('legalaid.media_code')
        matter_type1 = make_recipe('legalaid.matter_type1')
        matter_type2 = make_recipe('legalaid.matter_type2')

        data = {
            'matter_type1': matter_type1.code,
            'matter_type2': matter_type2.code,
            'media_code': media_code.code
        }
        response = self.client.patch(
            self.detail_url, data=data, format='json',
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCaseResponseKeys(response)

        case = self.case_obj
        case.matter_type1 = matter_type1
        case.matter_type2 = matter_type2
        case.media_code = media_code
        self.assertCaseEqual(response.data, case)

        self.assertNoLogInDB()
