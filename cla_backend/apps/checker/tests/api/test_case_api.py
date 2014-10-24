import uuid
from checker.serializers import CaseSerializer

from rest_framework import status
from rest_framework.test import APITestCase

from cla_eventlog.models import Log

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin

from legalaid.models import Case, PersonalDetails
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin
from cla_common.constants import CASE_SOURCE


class CaseTests(
    CLACheckerAuthBaseApiTestMixin, SimpleResourceAPIMixin, APITestCase
):
    LOOKUP_KEY = 'reference'
    API_URL_BASE_NAME = 'case'
    RESOURCE_RECIPE = 'legalaid.case'

    def make_resource(self):
        return None

    def assertEligibilityCheckResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['eligibility_check', 'personal_details', 'reference',
                'requires_action_at', 'outcome_code', 'adaptation_details']
        )

    def assertPersonalDetailsEqual(self, data, obj):
        if data is None or obj is None:
            self.assertEqual(data, obj)
        else:
            for prop in ['title', 'full_name', 'postcode', 'street', 'mobile_phone', 'home_phone']:
                self.assertEqual(unicode(getattr(obj, prop)), data[prop])

    def assertCaseEqual(self, data, case):
        self.assertEqual(case.reference, data['reference'])
        self.assertEqual(unicode(case.eligibility_check.reference), data['eligibility_check'])
        self.assertPersonalDetailsEqual(data['personal_details'], case.personal_details)

        self.assertEqual(Case.objects.count(), 1)
        case = Case.objects.first()
        self.assertEqual(case.source, CASE_SOURCE.WEB)

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        ### LIST
        self._test_delete_not_allowed(self.list_url)

    # CREATE

    def test_create_no_data(self):
        """
        CREATE should raise validation error when data is empty
        """
        response = self.client.post(
            self.list_url, data={}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertItemsEqual(
            response.data.keys(), ['eligibility_check', 'personal_details']
        )

        self.assertEqual(Case.objects.count(), 0)

    def test_create_with_data(self):
        check = make_recipe('legalaid.eligibility_check')

        data = {
            'eligibility_check': unicode(check.reference),
            'personal_details': {
                'title': 'MR',
                'full_name': 'John Doe',
                'postcode': 'SW1H 9AJ',
                'street': '102 Petty France',
                'mobile_phone': '0123456789',
                'home_phone': '9876543210',
            }
        }
        response = self.client.post(
            self.list_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEligibilityCheckResponseKeys(response)

        self.assertCaseEqual(response.data,
            Case(
                reference=response.data['reference'],
                eligibility_check=check,
                personal_details=PersonalDetails(**data['personal_details'])
            )
        )

        # test that the Case is in the db and created by 'web' user
        self.assertEqual(Case.objects.count(), 1)
        case = Case.objects.first()
        self.assertEqual(case.created_by.username, 'web')

        # test that the log is in the db and created by 'web' user
        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.first()
        self.assertEqual(log.created_by.username, 'web')

    def _test_method_in_error(self, method, url):
        """
        Generic method called by 'create' and 'patch' to test against validation
        errors.
        """
        invalid_uuid = str(uuid.uuid4())
        data={
            'eligibility_check': invalid_uuid,
            'personal_details': {
                "title": '1'*21,
                "full_name": None,
                "postcode": '1'*13,
                "street": '1'*256,
                "mobile_phone": '1'*21,
                "home_phone": '1'*21,
            }
        }

        method_callable = getattr(self.client, method)
        response = method_callable(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        errors = response.data
        self.assertItemsEqual(
            errors.keys(), ['eligibility_check', 'personal_details']
        )
        self.assertEqual(errors['eligibility_check'], [u'Object with reference=%s does not exist.' % invalid_uuid])
        self.assertItemsEqual(
            errors['personal_details'],
            [
                {
                    'title': [u'Ensure this value has at most 20 characters (it has 21).'],
                    'postcode': [u'Ensure this value has at most 12 characters (it has 13).'],
                    'street': [u'Ensure this value has at most 255 characters (it has 256).'],
                    'mobile_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
                    'home_phone': [u'Ensure this value has at most 20 characters (it has 21).'],
                }
            ]
        )

    def test_create_in_error(self):
        self._test_method_in_error('post', self.list_url)

    def test_cannot_create_with_other_reference(self):
        """
        Cannot create a case passing an eligibility check reference already assigned
        to another case
        """
        # create a different case
        case = make_recipe('legalaid.case')

        data = {
            'eligibility_check': unicode(case.eligibility_check.reference),
            'personal_details': {
                'title': 'MR',
                'full_name': 'John Doe',
                'postcode': 'SW1H 9AJ',
                'street': '102 Petty France',
                'mobile_phone': '0123456789',
                'home_phone': '9876543210',
            }
        }
        response = self.client.post(
            self.list_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.data,
            {'eligibility_check': [u'Case with this Eligibility check already exists.']}
        )

    def test_case_serializer_with_dupe_eligibility_check_reference(self):
        case = make_recipe('legalaid.case')

        data = {u'eligibility_check': case.eligibility_check.reference,
                u'personal_details': {u'full_name': u'John Doe',
                                      u'home_phone': u'9876543210',
                                      u'mobile_phone': u'0123456789',
                                      u'postcode': u'SW1H 9AJ',
                                      u'street': u'102 Petty France',
                                      u'title': u'MR'}}
        serializer = CaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertDictEqual(
            serializer.errors,
            {'eligibility_check':
                 [u'Case with this Eligibility check already exists.']})
