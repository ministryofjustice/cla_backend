from decimal import Decimal
import unittest
import datetime
from django.contrib.auth.models import User
import legalaid.utils.csvupload.validators as v
import re

from rest_framework import serializers
from rest_framework.test import APITestCase
from provider.oauth2.models import AccessToken

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from cla_provider.models import Staff


class CSVUploadAPIMixin(SimpleResourceAPIMixin):
    RESOURCE_RECIPE = 'cla_provider.csvupload_case'
    API_URL_BASE_NAME = 'csvupload'

    @property
    def response_keys(self):
        return [
            'id',
            'provider',
            'created_by',
            'comment',
            'rows',
            'month',
            'created',
        ]

    @property
    def response_keys_details(self):
        keys = self.response_keys[:]
        keys.remove('rows')
        keys.append('body')
        return keys

    def make_resource(self, **kwargs):
        kwargs.update(
            {
                'created_by': self.user.staff,
                'provider': self.provider
            }
        )
        return super(CSVUploadAPIMixin, self).make_resource(**kwargs)


class CSVUploadTestCase(CSVUploadAPIMixin,
                        CLAProviderAuthBaseApiTestMixin,
                        APITestCase):

    def setUp(self):
        super(CSVUploadTestCase, self).setUp()
        self.wrong_user = User.objects.create_user(
            'wrong user', 'wr@ng.user', 'password')
        self.wrong_provider = make_recipe('cla_provider.provider')
        self.wrong_provider.staff_set.add(
            Staff(user=self.wrong_user, is_manager=True))
        self.wrong_provider.save()

        # Create an access token from wrong user
        self.wrong_staff_token = AccessToken.objects.create(
            user=self.wrong_user,
            client=self.staff_api_client,
            token='wrong_stafF_token',
            scope=0
        )


    def assertResponseKeys(self, response, detail=False):
        return \
            super(CSVUploadTestCase, self).assertResponseKeys(
                response,
                keys=self.response_keys_details if detail else None)

    def test_get(self):
        response = self.client.get(
            self.detail_url,
            HTTP_AUTHORIZATION=self.get_http_authorization()
        )

        self.assertResponseKeys(
            response, detail=True
        )

    def test_get_list(self):
        response = \
            self.client.get(self.list_url,
                            HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertResponseKeys(response)

    def test_get_list_with_wrong_provider(self):
        response = \
            self.client.get(
                self.list_url,
                HTTP_AUTHORIZATION=self.get_http_authorization(token=self.wrong_staff_token))

        self.assertListEqual(response.data, [])

    def test_methods_not_authorized(self):
        self._test_get_not_authorized(self.list_url, self.invalid_token)
        self._test_get_not_authorized(self.detail_url, self.invalid_token)

    def test_methods_not_allowed(self):
        self._test_patch_not_allowed(self.detail_url, data={'anything': 'it doesn\'t matter'})


class ProviderCSVValidatorTestCase(unittest.TestCase):

    def setUp(self):
        self.data = [
            [u'3333333', u'0001', u'2B222B', u'A N Other', u'Corgi',
             u'02/01/1901', u'E', u'M', u'1', u'', u'', u'SW1A 1AA',
             u'X', u'EPRO', u'ESOS', u'EA', u'EB', u'', u'01/01/1901',
             u'01/01/1902', u'99', u'99.5', u'', u'ILL', u'0', u'0',
             u'', u'N', u'', u'', u'NAR', u'', u'DK', u'TA' ],

            [ u'2222222', u'0000', u'1A111A', u'A', u'Corgi', u'01/01/1901',
              u'D', u'F', u'1', u'', u'', u'SW1A 1AA', u'', u'EPRO',
              u'ESOS', u'', u'', u'', u'', u'', u'18', u'99.5', u'', u'MOB',
              u'', u'', u'FINI', u'', u'', u'', u'NAR', u'', u'', u'TA' ]
        ]

        self.dummy_cleaned_data = {
            'DOB': datetime.datetime(1901, 1, 2, 0, 0),
            'Media Code': u'DK', 'Exempted Reason Code': u'',
            'Telephone / Online': u'TA',
            'First Name': u'A N Other', 'Unused1': u'',
            'Stage Reached': u'EB', 'Unused3': u'', 'Unused2': u'',
            'Matter Type 1': u'EPRO', 'Matter Type 2': u'ESOS',
            'Exceptional Cases (ref)': u'', 'Time Spent': 99,
            'CLA Reference Number': 3333333, 'Client Ref': u'0001',
            'Determination': u'', 'Travel Costs': Decimal('0'),
            'Outcome Code': u'EB',
            'Date Opened': datetime.datetime(2014, 1, 1, 0, 0),
            'Signposting / Referral': u'',
            'Eligibility Code': u'X', 'Gender': u'M',
            'Case Costs': Decimal('99.5'),
            'Disbursements': Decimal('0'),
            'Disability Code': u'ILL',
            'Suitable for Telephone Advice': u'N',
            'Adjustments / Adaptations': u'',
            'Date Closed': datetime.datetime(2014, 1, 2, 0, 0),
            'Age Range': u'E', 'Surname': u'Corgi',
            'Account Number': u'2B222B', 'Unused4': u'',
            'Postcode': u'SW1A 1AA', 'Ethnicity': u'1'
        }

    def test_validator_valid(self):
        validator = v.ProviderCSVValidator(self.data)
        self.assertEqual(len(validator.validate()), 2)

    def test_invalid_field_count(self):
        validator = v.ProviderCSVValidator([[],[]])
        with self.assertRaisesRegexp(serializers.ValidationError,
                                     r'Row: 1 - Incorrect number of columns'):
            validator.validate()


    def test_closed_date_after_opened_date_invariant(self):
        validator = v.ProviderCSVValidator([
            [u'3333333', u'0001', u'2B222B', u'A N Other', u'Corgi',
             u'02/01/1901', u'E', u'M', u'1', u'', u'', u'SW1A 1AA',
             u'X', u'EADM', u'ESOS', u'EB', u'EB', u'', u'01/01/2014',
             u'01/01/1902', u'99', u'99.5', u'', u'ILL', u'0', u'0',
             u'', u'N', u'', u'', u'NAR', u'', u'DK', u'TA' ],
        ])
        with self.assertRaisesRegexp(serializers.ValidationError, 'Row: 1 - .*must be after'):
            validator.validate()

    def test_invalid_account_number(self):
        validator = v.ProviderCSVValidator([
            [u'3333333', u'0001',

             u'22222B',

             u'A N Other', u'Corgi',
             u'02/01/1901', u'E', u'M', u'1', u'', u'', u'SW1A 1AA',
             u'X', u'EPRO', u'ESOS', u'EB', u'EB', u'', u'01/01/1901',
             u'01/01/1902', u'99', u'99.5', u'', u'ILL', u'0', u'0',
             u'', u'N', u'', u'', u'NAR', u'', u'DK', u'TA' ],
        ])
        with self.assertRaises(serializers.ValidationError):
            validator.validate()


    def test_service_adapation_validation_valid(self):
        validator = v.ProviderCSVValidator([
            [u'3333333', u'0001', u'2B222B', u'A N Other', u'Corgi',
             u'02/01/1901', u'E', u'M', u'1', u'', u'', u'SW1A 1AA',
             u'X', u'EPRO', u'ESOS', u'EB', u'EB', u'', u'01/01/2014',
             u'02/01/2014', u'99', u'99.5', u'', u'ILL', u'0', u'0',
             u'', u'N', u'', u'',

             u'LOL',

             u'', u'DK', u'TA' ],
            ])
        with self.assertRaisesRegexp(serializers.ValidationError, r'Adjustments / Adaptations - LOL must be one of'):
            validator.validate()

    def test_service_adapation_validation_required(self):

        validator = v.ProviderCSVValidator(self.data)


        cleaned_data = self.dummy_cleaned_data.copy()

        cleaned_data['Adjustments / Adaptations '] = u''

        with self.assertRaisesRegexp(serializers.ValidationError, r'Adjustments / Adaptations field is required'):
            validator._validate_service_adaptation(cleaned_data)


    def test_eligibility_code_validation_required(self):

        validator = v.ProviderCSVValidator(self.data)


        cleaned_data = self.dummy_cleaned_data.copy()

        validator._validate_eligibility_code(cleaned_data)

        cleaned_data['Eligibility Code'] = u''

        with self.assertRaisesRegexp(serializers.ValidationError, r'Eligibility Code field is required'):
            validator._validate_eligibility_code(cleaned_data)

    def test_validate_ta_oa_ff_not_valid_for_edu_and_dis(self):

        validator = v.ProviderCSVValidator(self.data)
        cleaned_data = self.dummy_cleaned_data.copy()

        validator._validate_eligibility_code(cleaned_data)

        cleaned_data['Telephone / Online'] = u'FF'

        validator._validate_telephone_or_online_advice(cleaned_data, u'education')
        validator._validate_telephone_or_online_advice(cleaned_data, u'discrimination')

        with self.assertRaisesRegexp(serializers.ValidationError, r'.*code FF only valid for.*'):
            validator._validate_telephone_or_online_advice(cleaned_data, u'ssss')

    def test_eligibility_code_validation_time_spent_less_than_132(self):

        validator = v.ProviderCSVValidator(self.data)

        cleaned_data = self.dummy_cleaned_data.copy()
        cleaned_data['Eligibility Code'] = u'S'

        validator._validate_eligibility_code(cleaned_data)

        cleaned_data['Time Spent'] = 999

        with self.assertRaisesRegexp(serializers.ValidationError, r'The eligibility code .* you have entered is not valid'):
            validator._validate_eligibility_code(cleaned_data)


    def test_validation_time_spent_less_than_18(self):

        validator = v.ProviderCSVValidator(self.data)

        cleaned_data = self.dummy_cleaned_data.copy()
        cleaned_data['Eligibility Code'] = u'S'
        cleaned_data['Determination'] = False

        validator._validate_eligibility_code(cleaned_data)
        cleaned_data['Time Spent'] = 999

        with self.assertRaisesRegexp(serializers.ValidationError, r'The eligibility code .* you have entered is not valid with'):
            validator._validate_eligibility_code(cleaned_data)



    def test_validation_time_spent_more_than_18_with_determination_not_valid(self):

        validator = v.ProviderCSVValidator(self.data)

        cleaned_data = self.dummy_cleaned_data.copy()
        cleaned_data['Eligibility Code'] = u'S'
        cleaned_data['Determination'] = True

        cleaned_data['Time Spent'] = 9
        validator._validate_time_spent(cleaned_data, u'welfare')
        cleaned_data['Time Spent'] = 999

        with self.assertRaisesRegexp(serializers.ValidationError, "[u'Time spent (999) must not be greater than 42 minutes']"):
            validator._validate_time_spent(cleaned_data, u'discrimination')

        with self.assertRaisesRegexp(serializers.ValidationError, "[u'Time spent (999) must not be greater than 18 minutes']"):
            validator._validate_time_spent(cleaned_data, u'welfare')


    def test_validation_exemption_code_or_cla_ref_required(self):

        validator = v.ProviderCSVValidator(self.data)

        cleaned_data = self.dummy_cleaned_data.copy()
        cleaned_data['Date Opened'] = datetime.datetime(2014, 1, 1)
        cleaned_data['Exempted Code Reason'] = u'aa'
        cleaned_data['Determination'] = False

        validator._validate_exemption(cleaned_data, u'debt')

        cleaned_data['Date Opened'] = datetime.datetime(2014, 1, 2)

        with self.assertRaisesRegexp(
                serializers.ValidationError,
                "[u'An Exemption Reason can only be entered for Debt, Discrimination and Education matter]"):
            validator._validate_exemption(cleaned_data, u'welfare')

        cleaned_data['Exempted Code Reason'] = u''
        cleaned_data['CLA Reference Number'] = u''


        cleaned_data['Date Opened'] = datetime.datetime(2011, 1, 1)
        cleaned_data['Exceptional Cases (ref)'] = u'foo'

        validator._validate_exemption(cleaned_data, u'debt')
        cleaned_data['Exempted Code Reason'] = u'aa'
        with self.assertRaisesRegexp(
                serializers.ValidationError,
                "[u'An Exemption Reason can only be entered for Debt, Discrimination and Education matter]"):
            validator._validate_exemption(cleaned_data, u'welfare')

    def test_category_consistency_validation(self):

        validator = v.ProviderCSVValidator(self.data)

        cleaned_data = self.dummy_cleaned_data.copy()
        cleaned_data['Matter Type 1'] = u'S'
        cleaned_data['Matter Type 2'] = u'P'

        with self.assertRaisesRegexp(serializers.ValidationError, r'fields must be of the same category'):
            validator._validate_category_consistency(cleaned_data)


    def test_staged_reached_validate_required_mt1s(self):

        validator = v.ProviderCSVValidator(self.data)

        cleaned_data = self.dummy_cleaned_data.copy()
        cleaned_data['Matter Type 1'] = u'DMCA'
        cleaned_data['Stage Reached'] = u''

        with self.assertRaisesRegexp(serializers.ValidationError, r'.*is required because Matter Type 1: DMCA was specified.*'):
            validator._validate_stage_reached(cleaned_data)

    def test_staged_reached_validate_not_allowed_mt1s(self):

        validator = v.ProviderCSVValidator(self.data)

        cleaned_data = self.dummy_cleaned_data.copy()
        cleaned_data['Matter Type 1'] = u'WBAA'

        with self.assertRaisesRegexp(serializers.ValidationError, r'.*is not allowed because Matter Type 1: WBAA was specified.*'):
            validator._validate_stage_reached(cleaned_data)

    def test_gte_validator(self):
        gte_0 = v.validate_gte(0)

        self.assertEqual(1, gte_0(1))
        with self.assertRaisesRegexp(serializers.ValidationError, '.*must be > 0'):
            gte_0(-1)

    def test_validate_not_current_month(self):
        d = datetime.datetime(1901, 1, 1)

        self.assertEqual(d, v.validate_not_current_month(d))

        with self.assertRaisesRegexp(serializers.ValidationError, r'.*must not be from current month'):
            v.validate_not_current_month(datetime.datetime.now())

    def test_decimal_validator(self):
        self.assertEqual(Decimal('1.0'), v.validate_decimal('1.0'))
        with self.assertRaisesRegexp(serializers.ValidationError, r'Invalid literal'):
            v.validate_decimal('QQ')

    def test_integer_validator(self):
        self.assertEqual(1, v.validate_integer('1'))
        with self.assertRaises(serializers.ValidationError):
            v.validate_integer('Q')

    def test_present_validator(self):
        val = '123'
        self.assertEqual(val, v.validate_present(val))
        with self.assertRaises(serializers.ValidationError):
            v.validate_present('')

    def test_date_validator(self):
        val = '10/12/2014'
        self.assertEqual(datetime.datetime(2014, 12, 10), v.validate_date(val))
        with self.assertRaisesRegexp(serializers.ValidationError, r'is not a valid date'):
            v.validate_date('FOO BAR BAZ')

    def test_not_present_validator(self):
        self.assertEqual('', v.validate_not_present(''))
        with self.assertRaisesRegexp(serializers.ValidationError,
                                     'Field should not be present'):
            v.validate_not_present('qqq')

    def test_regex_validator(self):
        validator = v.validate_regex('foo', re.I)
        val = 'FOO'
        self.assertEqual(val, validator(val))

        with self.assertRaisesRegexp(serializers.ValidationError,
                                     '[u"Field value (BAR) doesn\'t match pattern: foo"]'):
            validator('BAR')

    def test_validate_in_iterable(self):
        test_in = v.validate_in({'a', 'b', 'c'})
        self.assertEqual('a', test_in('a'))

        with self.assertRaisesRegexp(serializers.ValidationError, r'.*must be one of'):
            test_in('q')

class DependsOnDecoratorTestCase(unittest.TestCase):

    def test_method_called(self):

        class Test1(object):
            @v.depends_on('a', check=v.TRUTHY)
            def do_something(self, d):
                return 1
        inst = Test1()
        self.assertEqual(1,
                         inst.do_something({'a': True})
        )

    def test_method_called_default_check_is_TRUTHY(self):

        class Test1(object):
            @v.depends_on('a')
            def do_something(self, d):
                return 1
        inst = Test1()
        self.assertEqual(1,
                         inst.do_something({'a': True})
        )


    def test_method_not_called(self):

        class Test1(object):
            @v.depends_on('a', check=v.FALSEY)
            def do_something(self, d):
                return 1
        inst = Test1()
        self.assertEqual(None,
                         inst.do_something({'a': True})
        )
