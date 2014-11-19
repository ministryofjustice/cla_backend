from decimal import Decimal
import unittest
import datetime
from django.contrib.auth.models import User
import legalaid.validators as v
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
             u'X', u'FFFF', u'QQQQ', u'QA', u'QM', u'', u'01/01/1901',
             u'01/01/1902', u'99', u'99.5', u'', u'ILL', u'0', u'0',
             u'', u'N', u'', u'', u'NAR', u'', u'DK', u'TA' ],

            [ u'2222222', u'0000', u'1A111A', u'A', u'Corgi', u'01/01/1901',
              u'D', u'F', u'1', u'', u'', u'SW1A 1AA', u'', u'SWAG',
              u'YOLO', u'', u'', u'', u'', u'', u'18', u'99.5', u'', u'MOB',
              u'', u'', u'AAAA', u'', u'', u'', u'NAR', u'', u'', u'TA' ]
        ]

    def test_validator_valid(self):
        validator = v.ProviderCSVValidator(self.data)
        self.assertEqual(len(validator.validate()), 2)

    def test_invalid_field_count(self):
        validator = v.ProviderCSVValidator([[],[]])
        with self.assertRaisesRegexp(serializers.ValidationError,
                                     r'Row: 1 - Incorrect number of columns'):
            validator.validate()


    def test_invalid_global_invariant(self):
        validator = v.ProviderCSVValidator([
            [u'3333333', u'0001', u'2B222B', u'A N Other', u'Corgi',
             u'02/01/1901', u'E', u'M', u'1', u'', u'', u'SW1A 1AA',
             u'X', u'FFFF', u'QQQQ', u'QA', u'QM', u'', u'01/01/2014',
             u'01/01/1902', u'99', u'99.5', u'', u'ILL', u'0', u'0',
             u'', u'N', u'', u'', u'NAR', u'', u'DK', u'TA' ],
        ])
        with self.assertRaisesRegexp(serializers.ValidationError, 'Row: 1 - .*must be after'):
            validator.validate()

    def test_invalid_account_number(self):
        validator = v.ProviderCSVValidator([
            [u'3333333', u'0001', u'22222B', u'A N Other', u'Corgi',
             u'02/01/1901', u'E', u'M', u'1', u'', u'', u'SW1A 1AA',
             u'X', u'FFFF', u'QQQQ', u'QA', u'QM', u'', u'01/01/1901',
             u'01/01/1902', u'99', u'99.5', u'', u'ILL', u'0', u'0',
             u'', u'N', u'', u'', u'NAR', u'', u'DK', u'TA' ],
        ])
        with self.assertRaises(serializers.ValidationError):
            validator.validate()

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
                                     'Field doesn\'t match'):
            validator('BAR')
