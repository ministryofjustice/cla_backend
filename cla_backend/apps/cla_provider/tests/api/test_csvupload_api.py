import datetime
import re
import unittest
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings
from provider.oauth2.models import AccessToken
from rest_framework import serializers
from rest_framework.test import APITestCase

import legalaid.utils.csvupload.validators as v
from cla_provider.models import Staff
from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin


class CSVUploadAPIMixin(SimpleResourceAPIMixin):
    RESOURCE_RECIPE = "cla_provider.csvupload_case"
    API_URL_BASE_NAME = "csvupload"

    @property
    def response_keys(self):
        return ["id", "provider", "created_by", "comment", "rows", "month", "created", "modified"]

    @property
    def response_keys_details(self):
        keys = self.response_keys[:]
        keys.remove("rows")
        keys.append("body")
        return keys

    def make_resource(self, **kwargs):
        kwargs.update({"created_by": self.user.staff, "provider": self.provider})
        return super(CSVUploadAPIMixin, self).make_resource(**kwargs)


class CSVUploadTestCase(CSVUploadAPIMixin, CLAProviderAuthBaseApiTestMixin, APITestCase):
    def setUp(self):
        super(CSVUploadTestCase, self).setUp()
        self.wrong_user = User.objects.create_user("wrong user", "wr@ng.user", "password")
        self.wrong_provider = make_recipe("cla_provider.provider")
        self.wrong_provider.staff_set.add(Staff(user=self.wrong_user, is_manager=True))
        self.wrong_provider.save()

        # Create an access token from wrong user
        self.wrong_staff_token = AccessToken.objects.create(
            user=self.wrong_user, client=self.staff_api_client, token="wrong_stafF_token", scope=0
        )

    def assertResponseKeys(self, response, detail=False, paginated=False):
        return super(CSVUploadTestCase, self).assertResponseKeys(
            response, keys=self.response_keys_details if detail else None, paginated=paginated
        )

    def test_get(self):
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertResponseKeys(response, detail=True)

    def test_get_list(self):
        response = self.client.get(self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertResponseKeys(response, paginated=True)

    def test_get_list_with_wrong_provider(self):
        response = self.client.get(
            self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization(token=self.wrong_staff_token)
        )

        self.assertListEqual(response.data["results"], [])

    def test_methods_not_authorized(self):
        self._test_get_not_authorized(self.list_url, self.invalid_token)
        self._test_get_not_authorized(self.detail_url, self.invalid_token)

    def test_methods_not_allowed(self):
        self._test_patch_not_allowed(self.detail_url, data={"anything": "it doesn't matter"})


class ProviderCSVValidatorTestCase(unittest.TestCase):
    def setUp(self):
        contract_2013_format_data = v.contract_2013_validators.copy()
        contract_2013_format_data["CLA Reference Number"] = u"3333333"
        contract_2013_format_data["Client Ref"] = u"0001"
        contract_2013_format_data["Account Number"] = u"2B222B"
        contract_2013_format_data["First Name"] = u"A N Other"
        contract_2013_format_data["Surname"] = u"Corgi"
        contract_2013_format_data["DOB"] = u"02/01/2014"
        contract_2013_format_data["Age Range"] = u"E"
        contract_2013_format_data["Gender"] = u"M"
        contract_2013_format_data["Ethnicity"] = u"1"
        contract_2013_format_data["Unused1"] = u""
        contract_2013_format_data["Unused2"] = u""
        contract_2013_format_data["Postcode"] = u"SW1A 1AA"
        contract_2013_format_data["Eligibility Code"] = u"X"
        contract_2013_format_data["Matter Type 1"] = u""
        contract_2013_format_data["Matter Type 2"] = u""
        contract_2013_format_data["Stage Reached"] = u""
        contract_2013_format_data["Outcome Code"] = u""
        contract_2013_format_data["Unused3"] = u""
        contract_2013_format_data["Date Opened"] = u"01/01/2014"
        contract_2013_format_data["Date Closed"] = u"01/01/2015"
        contract_2013_format_data["Time Spent"] = u"99"
        contract_2013_format_data["Case Costs"] = u"99.5"
        contract_2013_format_data["Unused4"] = u""
        contract_2013_format_data["Disability Code"] = u"ILL"
        contract_2013_format_data["Disbursements"] = u"0"
        contract_2013_format_data["Travel Costs"] = u"0"
        contract_2013_format_data["Determination"] = u""
        contract_2013_format_data["Suitable for Telephone Advice"] = u"N"
        contract_2013_format_data["Exceptional Cases (ref)"] = u""
        contract_2013_format_data["Exempted Reason Code"] = u""
        contract_2013_format_data["Adjustments / Adaptations"] = u"NAR"
        contract_2013_format_data["Signposting / Referral"] = u""
        contract_2013_format_data["Media Code"] = u"DK"
        contract_2013_format_data["Telephone / Online"] = u"TA"
        self.contract_2013_data = contract_2013_format_data

        contract_2018_format_data = v.contract_2018_validators.copy()
        contract_2018_format_data["CLA Reference Number"] = u"3333333"
        contract_2018_format_data["Client Ref"] = u"0001"
        contract_2018_format_data["Account Number"] = u"2B222B"
        contract_2018_format_data["First Name"] = u"A N Other"
        contract_2018_format_data["Surname"] = u"Corgi"
        contract_2018_format_data["DOB"] = u"02/01/2014"
        contract_2018_format_data["Age Range"] = u"E"
        contract_2018_format_data["Gender"] = u"M"
        contract_2018_format_data["Ethnicity"] = u"1"
        contract_2018_format_data["Postcode"] = u"SW1A 1AA"
        contract_2018_format_data["Eligibility Code"] = u"X"
        contract_2018_format_data["Matter Type 1"] = u""
        contract_2018_format_data["Matter Type 2"] = u""
        contract_2018_format_data["Stage Reached"] = u""
        contract_2018_format_data["Outcome Code"] = u""
        contract_2018_format_data["Date Opened"] = u"01/09/2018"
        contract_2018_format_data["Date Closed"] = u"01/10/2018"
        contract_2018_format_data["Time Spent"] = u"18"
        contract_2018_format_data["Case Costs"] = u"99.5"
        contract_2018_format_data["Fixed Fee Amount"] = u"65"
        contract_2018_format_data["Fixed Fee Code"] = u"LF"
        contract_2018_format_data["Disability Code"] = u"ILL"
        contract_2018_format_data["Disbursements"] = u"0"
        contract_2018_format_data["Travel Costs"] = u"0"
        contract_2018_format_data["Determination"] = u""
        contract_2018_format_data["Suitable for Telephone Advice"] = u"N"
        contract_2018_format_data["Exceptional Cases (ref)"] = u""
        contract_2018_format_data["Exempted Reason Code"] = u""
        contract_2018_format_data["Adjustments / Adaptations"] = u"NAR"
        contract_2018_format_data["Signposting / Referral"] = u""
        contract_2018_format_data["Media Code"] = u"DK"
        contract_2018_format_data["Telephone / Online"] = u"TA"
        self.contract_2018_data = contract_2018_format_data

    @staticmethod
    def get_provider_csv_validator(data=None):
        data_in_2013_format = [
            [
                u"3333333",
                u"0001",
                u"2B222B",
                u"A N Other",
                u"Corgi",
                u"02/01/2014",
                u"E",
                u"M",
                u"1",
                u"",
                u"",
                u"SW1A 1AA",
                u"X",
                u"EPRO",
                u"ESOS",
                u"EA",
                u"EB",
                u"",
                u"01/01/2014",
                u"01/01/2015",
                u"99",
                u"99.5",
                u"",
                u"ILL",
                u"0",
                u"0",
                u"",
                u"N",
                u"",
                u"",
                u"NAR",
                u"",
                u"DK",
                u"TA",
            ],
            [
                u"2222222",
                u"0000",
                u"1A111A",
                u"A",
                u"Corgi",
                u"01/01/2014",
                u"D",
                u"F",
                u"1",
                u"",
                u"",
                u"SW1A 1AA",
                u"",
                u"EPRO",
                u"ESOS",
                u"",
                u"",
                u"",
                u"",
                u"",
                u"18",
                u"99.5",
                u"",
                u"MOB",
                u"",
                u"",
                u"FINI",
                u"",
                u"",
                u"",
                u"NAR",
                u"",
                u"",
                u"TA",
            ],
        ]
        data_in_2018_format = [
            [
                u"3333333",
                u"0001",
                u"2B222B",
                u"A N Other",
                u"Corgi",
                u"02/01/2014",
                u"E",
                u"M",
                u"1",
                u"SW1A 1AA",
                u"X",
                u"EPRO",
                u"ESOS",
                u"EA",
                u"EB",
                u"01/01/2014",
                u"01/01/2015",
                u"99",
                u"99.5",
                u"",
                u"NA",
                u"ILL",
                u"0",
                u"0",
                u"",
                u"N",
                u"",
                u"",
                u"NAR",
                u"",
                u"DK",
                u"TA",
            ],
            [
                u"2222222",
                u"0000",
                u"1A111A",
                u"A",
                u"Corgi",
                u"01/01/2014",
                u"D",
                u"F",
                u"1",
                u"SW1A 1AA",
                u"",
                u"EPRO",
                u"ESOS",
                u"",
                u"",
                u"",
                u"",
                u"18",
                u"99.5",
                u"",
                u"NA",
                u"MOB",
                u"",
                u"",
                u"FINI",
                u"",
                u"",
                u"",
                u"NAR",
                u"",
                u"",
                u"TA",
            ],
        ]
        if data is None:
            data = data_in_2018_format if settings.CONTRACT_2018_ENABLED else data_in_2013_format
        return v.ProviderCSVValidator(data)

    @staticmethod
    def get_dummy_cleaned_data_copy():
        data_in_2013_format = {
            "DOB": datetime.datetime(2014, 1, 2, 0, 0),
            "Media Code": u"DK",
            "Exempted Reason Code": u"",
            "Telephone / Online": u"TA",
            "First Name": u"A N Other",
            "Unused1": u"",
            "Stage Reached": u"EB",
            "Unused3": u"",
            "Unused2": u"",
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Exceptional Cases (ref)": u"",
            "Time Spent": 99,
            "CLA Reference Number": 3333333,
            "Client Ref": u"0001",
            "Determination": u"",
            "Travel Costs": Decimal("0"),
            "Outcome Code": u"EB",
            "Date Opened": datetime.datetime(2014, 1, 1, 0, 0),
            "Signposting / Referral": u"",
            "Eligibility Code": u"X",
            "Gender": u"M",
            "Case Costs": Decimal("99.5"),
            "Disbursements": Decimal("0"),
            "Disability Code": u"ILL",
            "Suitable for Telephone Advice": u"N",
            "Adjustments / Adaptations": u"",
            "Date Closed": datetime.datetime(2014, 1, 2, 0, 0),
            "Age Range": u"E",
            "Surname": u"Corgi",
            "Account Number": u"2B222B",
            "Unused4": u"",
            "Postcode": u"SW1A 1AA",
            "Ethnicity": u"1",
        }
        data_in_2018_format = {
            "DOB": datetime.datetime(2014, 1, 2, 0, 0),
            "Media Code": u"DK",
            "Exempted Reason Code": u"",
            "Telephone / Online": u"TA",
            "First Name": u"A N Other",
            "Stage Reached": u"EB",
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Exceptional Cases (ref)": u"",
            "Time Spent": 99,
            "CLA Reference Number": 3333333,
            "Client Ref": u"0001",
            "Determination": u"",
            "Travel Costs": Decimal("0"),
            "Outcome Code": u"EB",
            "Date Opened": datetime.datetime(2014, 1, 1, 0, 0),
            "Signposting / Referral": u"",
            "Eligibility Code": u"X",
            "Gender": u"M",
            "Case Costs": Decimal("99.5"),
            "Disbursements": Decimal("0"),
            "Disability Code": u"ILL",
            "Suitable for Telephone Advice": u"N",
            "Adjustments / Adaptations": u"",
            "Date Closed": datetime.datetime(2014, 1, 2, 0, 0),
            "Age Range": u"E",
            "Surname": u"Corgi",
            "Account Number": u"2B222B",
            "Postcode": u"SW1A 1AA",
            "Ethnicity": u"1",
            "Fixed Fee Amount": u"LF",
            "Fixed Fee Code": u"65",
        }
        data = data_in_2018_format if settings.CONTRACT_2018_ENABLED else data_in_2013_format
        return data.copy()

    @override_settings(CONTRACT_2018_ENABLED=False)
    def test_validator_valid_2013(self):
        validator = self.get_provider_csv_validator()
        self.assertEqual(len(validator.validate()), 2)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_valid_2018(self):
        validator = self.get_provider_csv_validator()
        self.assertEqual(len(validator.validate()), 2)

    def test_invalid_field_count(self):
        validator = self.get_provider_csv_validator([[], []])
        with self.assertRaisesRegexp(serializers.ValidationError, r"Row: 1 - Incorrect number of columns"):
            validator.validate()

    def test_closed_date_after_opened_date_invariant(self):
        test_values = {
            "Matter Type 1": u"EADM",
            "Matter Type 2": u"ESOS",
            "Stage Reached": u"EB",
            "Outcome Code": u"EB",
            "Date Opened": u"02/01/2014",
            "Date Closed": u"01/01/2014",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        with self.assertRaisesRegexp(serializers.ValidationError, "Row: 1 - .*must be after"):
            validator.validate()

    def test_invalid_account_number(self):
        test_values = {
            "Account Number": u"22222B",
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Stage Reached": u"EB",
            "Outcome Code": u"EB",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        with self.assertRaises(serializers.ValidationError):
            validator.validate()

    def test_service_adapation_validation_valid(self):
        test_values = {
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Stage Reached": u"EB",
            "Outcome Code": u"EB",
            "Adjustments / Adaptations": u"LOL",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        with self.assertRaisesRegexp(serializers.ValidationError, r"Adjustments / Adaptations - LOL must be one of"):
            validator.validate()

    @override_settings(CONTRACT_2018_ENABLED=False)
    def test_allowed_no_outcome_code_and_dates_if_determination_code_2013(self):
        test_values = {
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Date Opened": u"",
            "Date Closed": u"",
            "Time Spent": u"18",
            "Determination": u"FINI",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        try:
            validator.validate()
        except serializers.ValidationError:
            self.fail("Should not need outcome code or closed and opened dated if determination code present")

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_allowed_no_outcome_code_and_dates_if_determination_code_2018(self):
        test_values = {
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Date Opened": u"",
            "Date Closed": u"",
            "Fixed Fee Code": u"NA",
            "Time Spent": u"18",
            "Determination": u"FINI",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        try:
            validator.validate()
        except serializers.ValidationError:
            self.fail("Should not need outcome code or closed and opened dated if determination code present")

    def test_service_adapation_validation_required(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Adjustments / Adaptations "] = u""
        with self.assertRaisesRegexp(serializers.ValidationError, r"Adjustments / Adaptations field is required"):
            validator._validate_service_adaptation(cleaned_data)

    def test_eligibility_code_validation_required(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        validator._validate_eligibility_code(cleaned_data)
        cleaned_data["Eligibility Code"] = u""
        with self.assertRaisesRegexp(serializers.ValidationError, r"Eligibility Code field is required"):
            validator._validate_eligibility_code(cleaned_data)

    def test_validate_ta_oa_ff_not_valid_for_edu_and_dis(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        validator._validate_eligibility_code(cleaned_data)
        cleaned_data["Telephone / Online"] = u"FF"
        validator._validate_telephone_or_online_advice(cleaned_data, u"education")
        validator._validate_telephone_or_online_advice(cleaned_data, u"discrimination")
        with self.assertRaisesRegexp(serializers.ValidationError, r".*code FF only valid for.*"):
            validator._validate_telephone_or_online_advice(cleaned_data, u"ssss")

    def test_eligibility_code_validation_time_spent_less_than_132(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = u"S"
        validator._validate_eligibility_code(cleaned_data)
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, r"The eligibility code .* you have entered is not valid"
        ):
            validator._validate_eligibility_code(cleaned_data)

    def test_validation_time_spent_less_than_18(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = u"S"
        cleaned_data["Determination"] = False
        validator._validate_eligibility_code(cleaned_data)
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, r"The eligibility code .* you have entered is not valid with"
        ):
            validator._validate_eligibility_code(cleaned_data)

    def test_validation_time_spent_more_than_18_with_determination_not_valid(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = u"S"
        cleaned_data["Determination"] = True
        cleaned_data["Time Spent"] = 12
        validator._validate_time_spent(cleaned_data, u"welfare")
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, "[u'Time spent (999) must not be greater than 42 minutes']"
        ):
            validator._validate_time_spent(cleaned_data, u"discrimination")

        with self.assertRaisesRegexp(
            serializers.ValidationError, "[u'Time spent (999) must not be greater than 18 minutes']"
        ):
            validator._validate_time_spent(cleaned_data, u"welfare")

        cleaned_data["Time Spent"] = 9
        with self.assertRaisesRegexp(serializers.ValidationError, "[u'Time spent (9) must be in 6 minute intervals']"):
            validator._validate_time_spent(cleaned_data, u"welfare")

    def test_validation_exemption_code_or_cla_ref_required(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Date Opened"] = datetime.datetime(2014, 1, 1)
        cleaned_data["Exempted Code Reason"] = u"aa"
        cleaned_data["Determination"] = False
        validator._validate_exemption(cleaned_data, u"debt")
        cleaned_data["Date Opened"] = datetime.datetime(2014, 1, 2)

        with self.assertRaisesRegexp(
            serializers.ValidationError,
            "[u'An Exemption Reason can only be entered for Debt, Discrimination and Education matter]",
        ):
            validator._validate_exemption(cleaned_data, u"welfare")

        cleaned_data["Exempted Code Reason"] = u""
        cleaned_data["CLA Reference Number"] = u""
        cleaned_data["Date Opened"] = datetime.datetime(2011, 1, 1)
        cleaned_data["Exceptional Cases (ref)"] = u"foo"

        validator._validate_exemption(cleaned_data, u"debt")
        cleaned_data["Exempted Code Reason"] = u"aa"
        with self.assertRaisesRegexp(
            serializers.ValidationError,
            "[u'An Exemption Reason can only be entered for Debt, Discrimination and Education matter]",
        ):
            validator._validate_exemption(cleaned_data, u"welfare")

    def test_category_consistency_validation(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Matter Type 1"] = u"S"
        cleaned_data["Matter Type 2"] = u"P"
        with self.assertRaisesRegexp(serializers.ValidationError, r"fields must be of the same category"):
            validator._validate_category_consistency(cleaned_data)

    def test_staged_reached_validate_required_mt1s(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Matter Type 1"] = u"DMCA"
        cleaned_data["Stage Reached"] = u""
        with self.assertRaisesRegexp(
            serializers.ValidationError, r".*is required because Matter Type 1: DMCA was specified.*"
        ):
            validator._validate_stage_reached(cleaned_data)

    def test_staged_reached_validate_not_allowed_mt1s(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Matter Type 1"] = u"WBAA"
        with self.assertRaisesRegexp(
            serializers.ValidationError, r".*is not allowed because Matter Type 1: WBAA was specified.*"
        ):
            validator._validate_stage_reached(cleaned_data)

    def test_gte_validator(self):
        gte_0 = v.validate_gte(0)

        self.assertEqual(1, gte_0(1))
        with self.assertRaisesRegexp(serializers.ValidationError, ".*must be > 0"):
            gte_0(-1)

    def test_validate_not_current_month(self):
        d = datetime.datetime(2014, 1, 1)

        self.assertEqual(d, v.validate_not_current_month(d))

        with self.assertRaisesRegexp(serializers.ValidationError, r".*must not be from current month"):
            v.validate_not_current_month(datetime.datetime.now())

    def test_decimal_validator(self):
        self.assertEqual(Decimal("1.0"), v.validate_decimal("1.0"))
        with self.assertRaisesRegexp(serializers.ValidationError, r"Invalid literal"):
            v.validate_decimal("QQ")

    def test_integer_validator(self):
        self.assertEqual(1, v.validate_integer("1"))
        with self.assertRaises(serializers.ValidationError):
            v.validate_integer("Q")

    def test_present_validator(self):
        val = "123"
        self.assertEqual(val, v.validate_present(val))
        with self.assertRaises(serializers.ValidationError):
            v.validate_present("")

    def test_date_validator(self):
        val = "10/12/2014"
        self.assertEqual(datetime.datetime(2014, 12, 10), v.validate_date(val))
        with self.assertRaisesRegexp(serializers.ValidationError, r"is not a valid date"):
            v.validate_date("FOO BAR BAZ")

    def test_not_present_validator(self):
        self.assertEqual("", v.validate_not_present(""))
        with self.assertRaisesRegexp(serializers.ValidationError, "Field should not be present"):
            v.validate_not_present("qqq")

    def test_regex_validator(self):
        validator = v.validate_regex("foo", re.I)
        val = "FOO"
        self.assertEqual(val, validator(val))

        with self.assertRaisesRegexp(
            serializers.ValidationError, '[u"Field value (BAR) doesn\'t match pattern: foo"]'
        ):
            validator("BAR")

    def test_validate_in_iterable(self):
        test_in = v.validate_in({"a", "b", "c"})
        self.assertEqual("a", test_in("a"))

        with self.assertRaisesRegexp(serializers.ValidationError, r".*must be one of"):
            test_in("q")

    def _generate_contract_data_row(self, override=None):
        row = self.contract_2018_data.copy() if settings.CONTRACT_2018_ENABLED else self.contract_2013_data.copy()
        if override:
            row.update(override)
        return [val for key, val in row.items()]

    def _test_generated_contract_row_validates(self, override):
        data = [self._generate_contract_data_row(override)]
        validator = v.ProviderCSVValidator(data)
        try:
            validator.validate()
        except (serializers.ValidationError, Exception) as e:
            self.fail("{}".format(e))

    def _test_generated_2018_contract_row_validate_fails(self, override, expected_error):
        data = [self._generate_contract_data_row(override)]
        validator = v.ProviderCSVValidator(data)
        try:
            validator.validate()
        except (serializers.ValidationError, Exception) as e:
            if expected_error not in e.messages:
                self.fail("{}".format(e))

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_debt_outcome_code_DAA_is_valid(self):
        test_values = {
            "Matter Type 1": u"DPDE",
            "Matter Type 2": u"DVAL",
            "Stage Reached": u"DA",
            "Outcome Code": u"DAA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_family_outcome_code_FAA_is_valid(self):
        test_values = {"Matter Type 1": u"FAMA", "Matter Type 2": u"FADV", "Outcome Code": u"FAA"}
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_family_outcome_code_FAB_is_valid(self):
        test_values = {"Matter Type 1": u"FAMA", "Matter Type 2": u"FADV", "Outcome Code": u"FAB"}
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_family_outcome_code_FAC_is_valid(self):
        test_values = {"Matter Type 1": u"FAMA", "Matter Type 2": u"FADV", "Outcome Code": u"FAC"}
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_discrimination_outcome_code_QAA_is_valid(self):
        test_values = {
            "Matter Type 1": u"QPRO",
            "Matter Type 2": u"QAGE",
            "Stage Reached": u"QA",
            "Outcome Code": u"QAA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_fafa_determination_code_is_valid(self):
        test_values = {
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Stage Reached": u"EA",
            "Determination": u"FAFA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_exem_determination_code_is_valid(self):
        test_values = {
            "Matter Type 1": u"EPRO",
            "Matter Type 2": u"ESOS",
            "Stage Reached": u"EA",
            "Determination": u"EXEM",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_housing_outcome_code_haa_is_valid(self):
        test_values = {
            "Matter Type 1": u"HRNT",
            "Matter Type 2": u"HPRI",
            "Stage Reached": u"HA",
            "Outcome Code": u"HAA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_housing_outcome_code_hac_is_valid(self):
        test_values = {
            "Matter Type 1": u"HRNT",
            "Matter Type 2": u"HPRI",
            "Stage Reached": u"HA",
            "Outcome Code": u"HAC",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_housing_outcome_code_hab_is_valid(self):
        test_values = {
            "Matter Type 1": u"HRNT",
            "Matter Type 2": u"HPRI",
            "Stage Reached": u"HA",
            "Outcome Code": u"HAB",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_fixed_fee_amount_present(self):
        test_values = {
            "Matter Type 1": u"DMAP",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"130",
            "Fixed Fee Code": u"LF",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_fixed_fee_amount_missing(self):
        test_values = {
            "Matter Type 1": u"DMAP",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"",
            "Fixed Fee Code": u"HF",
        }
        expected_error = u"Row: 1 - Fixed Fee Amount must be entered for Fixed Fee Code (HF)"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_lower_fixed_fee_time_spent(self):
        test_values = {
            "Matter Type 1": u"DTOT",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"65",
            "Fixed Fee Code": u"LF",
            "Time Spent": u"66",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_lower_fixed_fee_excess_time_spent(self):
        test_values = {
            "Matter Type 1": u"DTOT",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"65",
            "Fixed Fee Code": u"LF",
            "Time Spent": u"133",
        }
        expected_error = u"Row: 1 - Time spent must be less than 133 minutes for LF fixed fee code"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_higher_fixed_fee_time_spent(self):
        test_values = {
            "Eligibility Code": u"V",
            "Matter Type 1": u"DMAP",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"130",
            "Fixed Fee Code": u"HF",
            "Time Spent": u"144",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_higher_fixed_fee_excess_time_spent(self):
        test_values = {
            "Eligibility Code": u"V",
            "Matter Type 1": u"DMAP",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"130",
            "Fixed Fee Code": u"HF",
            "Time Spent": u"900",
        }
        # TODO Clarify spec: are LF and HF both inclusive of 133?
        expected_error = u"Row: 1 - Time spent must be >=133 and <900 minutes for HF fixed fee code"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_higher_fixed_fee_insufficient_time_spent(self):
        test_values = {
            "Eligibility Code": u"V",
            "Matter Type 1": u"DMAP",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"130",
            "Fixed Fee Code": u"HF",
            "Time Spent": u"132",
        }
        expected_error = u"Row: 1 - Time spent must be >=133 and <900 minutes for HF fixed fee code"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_misc_rate_fixed_fee(self):
        test_values = {"Matter Type 1": u"MSCB", "Fixed Fee Amount": u"", "Fixed Fee Code": u"MR"}
        # TODO complete then Matter Type 1 MSCB added
        self._test_generated_2018_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_hwfm_rate_fixed_fee(self):
        test_values = {
            "Matter Type 1": u"FAMY",
            "Matter Type 2": u"FMEC",
            "Fixed Fee Amount": u"119.6",
            "Fixed Fee Code": u"HM",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_mt1_fixed_fee_code_mismatch(self):
        test_values = {
            "Matter Type 1": u"FAMY",
            "Matter Type 2": u"FMEC",
            "Fixed Fee Amount": u"119.6",
            "Fixed Fee Code": u"LF",
        }
        expected_error = u"Row: 1 - The HM fee code should be used where Matter Type 1 Code - FAMY is used"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_hourly_rate_hr_fixed_fee_code(self):
        test_values = {
            "Matter Type 1": u"DMAP",
            "Matter Type 2": u"DOTH",
            "Stage Reached": u"DB",
            "Fixed Fee Amount": u"119.6",
            "Fixed Fee Code": u"HR",
        }
        self._test_generated_contract_row_validates(override=test_values)


class DependsOnDecoratorTestCase(unittest.TestCase):
    def test_method_called(self):
        class Test1(object):
            @v.depends_on("a", check=v.value_is_truthy)
            def do_something(self, d):
                return 1

        inst = Test1()
        self.assertEqual(1, inst.do_something({"a": True}))

    def test_method_called_default_check_is_TRUTHY(self):
        class Test1(object):
            @v.depends_on("a")
            def do_something(self, d):
                return 1

        inst = Test1()
        self.assertEqual(1, inst.do_something({"a": True}))

    def test_method_not_called(self):
        class Test1(object):
            @v.depends_on("a", check=v.value_is_falsey)
            def do_something(self, d):
                return 1

        inst = Test1()
        self.assertEqual(None, inst.do_something({"a": True}))
