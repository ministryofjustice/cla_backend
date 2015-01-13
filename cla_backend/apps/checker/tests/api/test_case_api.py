import datetime
import uuid

from django.utils import timezone
from django.core import mail

from checker.serializers import CaseSerializer

from rest_framework import status
from rest_framework.test import APITestCase

from cla_eventlog.models import Log

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin

from legalaid.models import Case, PersonalDetails
from legalaid.tests.views.test_base import CLACheckerAuthBaseApiTestMixin
from cla_common.constants import CASE_SOURCE


class BaseCaseTestCase(
    CLACheckerAuthBaseApiTestMixin, SimpleResourceAPIMixin, APITestCase
):
    LOOKUP_KEY = 'reference'
    API_URL_BASE_NAME = 'case'
    RESOURCE_RECIPE = 'legalaid.case'

    def make_resource(self):
        return None

    def assertCaseResponseKeys(self, response):
        self.assertItemsEqual(
            response.data.keys(),
            ['eligibility_check', 'personal_details', 'reference',
                'requires_action_at', 'adaptation_details']
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

    def get_personal_details_default_post_data(self):
        return {
            'title': 'MR',
            'full_name': 'John Doe',
            'postcode': 'SW1H 9AJ',
            'street': '102 Petty France',
            'mobile_phone': '0123456789',
            'home_phone': '9876543210',
        }


class CaseTestCase(BaseCaseTestCase):
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
            response.data.keys(), ['personal_details']
        )

        self.assertEqual(Case.objects.count(), 0)

    def test_create_with_data(self):
        check = make_recipe('legalaid.eligibility_check')

        data = {
            'eligibility_check': unicode(check.reference),
            'personal_details': self.get_personal_details_default_post_data()
        }
        response = self.client.post(
            self.list_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

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

        # no email sent
        self.assertEquals(len(mail.outbox), 0)

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
            'personal_details': self.get_personal_details_default_post_data()
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

        data = {
            u'eligibility_check': case.eligibility_check.reference,
            u'personal_details': self.get_personal_details_default_post_data()
        }
        serializer = CaseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertDictEqual(
            serializer.errors,
            {'eligibility_check':
                 [u'Case with this Eligibility check already exists.']})


class CallMeBackCaseTestCase(BaseCaseTestCase):
    @property
    def _default_dt(self):
        if not hasattr(self, '__default_dt'):
            now = timezone.now()
            dt = now + datetime.timedelta(days=7-now.weekday())
            self.__default_dt = dt.replace(
                hour=10, minute=0, second=0, microsecond=0
            )
        return self.__default_dt

    def test_create_with_callmeback(self):
        self.assertEquals(len(mail.outbox), 0)

        check = make_recipe('legalaid.eligibility_check')

        data = {
            'eligibility_check': unicode(check.reference),
            'personal_details': self.get_personal_details_default_post_data(),
            'requires_action_at': self._default_dt.isoformat()
        }
        response = self.client.post(
            self.list_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

        case = Case.objects.first()
        self.assertEqual(case.requires_action_at, self._default_dt)
        self.assertEqual(case.callback_attempt, 1)
        self.assertEqual(case.outcome_code, 'CB1')
        self.assertEqual(case.source, CASE_SOURCE.WEB)
        self.assertEqual(case.log_set.count(), 2)

        self.assertEqual(case.log_set.filter(code='CB1').count(), 1)
        log = case.log_set.get(code='CB1')

        self.assertEqual(
            log.notes,
            'Callback scheduled for %s. ' % (
                timezone.localtime(self._default_dt).strftime("%d/%m/%Y %H:%M")
            )
        )
        self.assertEqual(log.context, {
            'requires_action_at': self._default_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'sla_120': (self._default_dt + datetime.timedelta(minutes=120)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'sla_15': (self._default_dt + datetime.timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ')
        })

        # checking email
        self.assertEquals(len(mail.outbox), 1)

    def test_create_should_ignore_outcome_code(self):
        """
        Here only to check backward incompatibility
        """
        check = make_recipe('legalaid.eligibility_check')

        data = {
            'eligibility_check': unicode(check.reference),
            'personal_details': self.get_personal_details_default_post_data(),
            'requires_action_at': self._default_dt.isoformat(),
            'outcome_code': 'TEST'
        }
        response = self.client.post(
            self.list_url, data=data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCaseResponseKeys(response)

        case = Case.objects.first()
        self.assertNotEqual(case.outcome_code, 'TEST')
