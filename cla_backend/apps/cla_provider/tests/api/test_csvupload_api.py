import datetime
import re
import unittest
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings
from oauth2_provider.models import AccessToken
from rest_framework import serializers
from rest_framework.test import APITestCase

import legalaid.utils.csvupload.validators as v
from legalaid.utils.csvupload.contracts import (
    CONTRACT_EIGHTEEN_DISCRIMINATION,
    CONTRACT_EIGHTEEN_EDUCATION,
    contract_2018_category_spec,
    get_applicable_contract,
)
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
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=2)
        # Create an access token from wrong user
        self.wrong_staff_token = AccessToken.objects.create(
            user=self.wrong_user,
            application=self.staff_api_client,
            token="wrong_stafF_token",
            scope=0,
            expires=expiry_date,
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
        contract_2013_format_data = v.contract_2013_validators_for_original_field_order.copy()
        contract_2013_format_data["CLA Reference Number"] = "3333333"
        contract_2013_format_data["Client Ref"] = "0001"
        contract_2013_format_data["Account Number"] = "2B222B"
        contract_2013_format_data["First Name"] = "A N Other"
        contract_2013_format_data["Surname"] = "Corgi"
        contract_2013_format_data["DOB"] = "02/01/2014"
        contract_2013_format_data["Age Range"] = "E"
        contract_2013_format_data["Gender"] = "M"
        contract_2013_format_data["Ethnicity"] = "1"
        contract_2013_format_data["Unused1"] = ""
        contract_2013_format_data["Unused2"] = ""
        contract_2013_format_data["Postcode"] = "SW1A 1AA"
        contract_2013_format_data["Eligibility Code"] = "X"
        contract_2013_format_data["Matter Type 1"] = ""
        contract_2013_format_data["Matter Type 2"] = ""
        contract_2013_format_data["Stage Reached"] = ""
        contract_2013_format_data["Outcome Code"] = ""
        contract_2013_format_data["Unused3"] = ""
        contract_2013_format_data["Date Opened"] = "01/01/2014"
        contract_2013_format_data["Date Closed"] = "01/01/2015"
        contract_2013_format_data["Time Spent"] = "99"
        contract_2013_format_data["Case Costs"] = "99.5"
        contract_2013_format_data["Unused4"] = ""
        contract_2013_format_data["Disability Code"] = "ILL"
        contract_2013_format_data["Disbursements"] = "0"
        contract_2013_format_data["Travel Costs"] = "0"
        contract_2013_format_data["Determination"] = ""
        contract_2013_format_data["Suitable for Telephone Advice"] = "N"
        contract_2013_format_data["Exceptional Cases (ref)"] = ""
        contract_2013_format_data["Exempted Reason Code"] = ""
        contract_2013_format_data["Adjustments / Adaptations"] = "NAR"
        contract_2013_format_data["Signposting / Referral"] = ""
        contract_2013_format_data["Media Code"] = "DK"
        contract_2013_format_data["Telephone / Online"] = "TA"
        self.contract_2013_data = contract_2013_format_data

        contract_2018_format_data = v.contract_2018_validators_for_new_field_order.copy()
        contract_2018_format_data["CLA Reference Number"] = "3333333"
        contract_2018_format_data["Client Ref"] = "0001"
        contract_2018_format_data["Account Number"] = "2B222B"
        contract_2018_format_data["First Name"] = "A N Other"
        contract_2018_format_data["Surname"] = "Corgi"
        contract_2018_format_data["DOB"] = "02/01/2014"
        contract_2018_format_data["Age Range"] = "E"
        contract_2018_format_data["Gender"] = "M"
        contract_2018_format_data["Ethnicity"] = "1"
        contract_2018_format_data["Postcode"] = "SW1A 1AA"
        contract_2018_format_data["Eligibility Code"] = "X"
        contract_2018_format_data["Matter Type 1"] = ""
        contract_2018_format_data["Matter Type 2"] = ""
        contract_2018_format_data["Stage Reached"] = ""
        contract_2018_format_data["Outcome Code"] = ""
        contract_2018_format_data["Date Opened"] = "01/09/2018"
        contract_2018_format_data["Date Closed"] = "01/10/2018"
        contract_2018_format_data["Time Spent"] = "18"
        contract_2018_format_data["Case Costs"] = "99.5"
        contract_2018_format_data["Fixed Fee Amount"] = "65"
        contract_2018_format_data["Fixed Fee Code"] = "LF"
        contract_2018_format_data["Disability Code"] = "ILL"
        contract_2018_format_data["Disbursements"] = "0"
        contract_2018_format_data["Travel Costs"] = "0"
        contract_2018_format_data["Determination"] = ""
        contract_2018_format_data["Suitable for Telephone Advice"] = "N"
        contract_2018_format_data["Exceptional Cases (ref)"] = ""
        contract_2018_format_data["Exempted Reason Code"] = ""
        contract_2018_format_data["Adjustments / Adaptations"] = "NAR"
        contract_2018_format_data["Signposting / Referral"] = ""
        contract_2018_format_data["Media Code"] = "DK"
        contract_2018_format_data["Telephone / Online"] = "TA"
        self.contract_2018_data = contract_2018_format_data

    @staticmethod
    def get_provider_csv_validator(data=None):
        data_in_2013_format = [
            [
                "3333333",
                "0001",
                "2B222B",
                "A N Other",
                "Corgi",
                "02/01/2014",
                "E",
                "M",
                "1",
                "",
                "",
                "SW1A 1AA",
                "X",
                "EPRO",
                "ESOS",
                "EA",
                "EB",
                "",
                "01/01/2014",
                "01/01/2015",
                "99",
                "99.5",
                "",
                "ILL",
                "0",
                "0",
                "",
                "N",
                "",
                "",
                "NAR",
                "",
                "DK",
                "TA",
            ],
            [
                "2222222",
                "0000",
                "1A111A",
                "A",
                "Corgi",
                "01/01/2014",
                "D",
                "F",
                "1",
                "",
                "",
                "SW1A 1AA",
                "",
                "EPRO",
                "ESOS",
                "",
                "",
                "",
                "",
                "",
                "18",
                "99.5",
                "",
                "MOB",
                "",
                "",
                "FINI",
                "",
                "",
                "",
                "NAR",
                "",
                "",
                "TA",
            ],
        ]
        data_in_2018_format = [
            [
                "3333333",
                "0001",
                "2B222B",
                "A N Other",
                "Corgi",
                "02/01/2014",
                "E",
                "M",
                "1",
                "SW1A 1AA",
                "X",
                "EPRO",
                "ESOS",
                "EA",
                "EB",
                "01/01/2014",
                "01/01/2015",
                "99",
                "99.5",
                "",
                "NA",
                "ILL",
                "0",
                "0",
                "",
                "N",
                "",
                "",
                "NAR",
                "",
                "DK",
                "TA",
            ],
            [
                "2222222",
                "0000",
                "1A111A",
                "A",
                "Corgi",
                "01/01/2014",
                "D",
                "F",
                "1",
                "SW1A 1AA",
                "",
                "EPRO",
                "ESOS",
                "",
                "",
                "",
                "",
                "18",
                "99.5",
                "",
                "NA",
                "MOB",
                "",
                "",
                "FINI",
                "",
                "",
                "",
                "NAR",
                "",
                "",
                "TA",
            ],
        ]
        if data is None:
            data = data_in_2018_format if settings.CONTRACT_2018_ENABLED else data_in_2013_format
        return v.ProviderCSVValidator(data)

    @staticmethod
    def get_dummy_cleaned_data_copy():
        data_in_2013_format = {
            "DOB": datetime.datetime(2014, 1, 2, 0, 0),
            "Media Code": "DK",
            "Exempted Reason Code": "",
            "Telephone / Online": "TA",
            "First Name": "A N Other",
            "Unused1": "",
            "Stage Reached": "EB",
            "Unused3": "",
            "Unused2": "",
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Exceptional Cases (ref)": "",
            "Time Spent": 99,
            "CLA Reference Number": 3333333,
            "Client Ref": "0001",
            "Determination": "",
            "Travel Costs": Decimal("0"),
            "Outcome Code": "EB",
            "Date Opened": datetime.datetime(2014, 1, 1, 0, 0),
            "Signposting / Referral": "",
            "Eligibility Code": "X",
            "Gender": "M",
            "Case Costs": Decimal("99.5"),
            "Disbursements": Decimal("0"),
            "Disability Code": "ILL",
            "Suitable for Telephone Advice": "N",
            "Adjustments / Adaptations": "",
            "Date Closed": datetime.datetime(2014, 1, 2, 0, 0),
            "Age Range": "E",
            "Surname": "Corgi",
            "Account Number": "2B222B",
            "Unused4": "",
            "Postcode": "SW1A 1AA",
            "Ethnicity": "1",
        }
        data_in_2018_format = {
            "DOB": datetime.datetime(2014, 1, 2, 0, 0),
            "Media Code": "DK",
            "Exempted Reason Code": "",
            "Telephone / Online": "TA",
            "First Name": "A N Other",
            "Stage Reached": "EB",
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Exceptional Cases (ref)": "",
            "Time Spent": 99,
            "CLA Reference Number": 3333333,
            "Client Ref": "0001",
            "Determination": "",
            "Travel Costs": Decimal("0"),
            "Outcome Code": "EB",
            "Date Opened": datetime.datetime(2014, 1, 1, 0, 0),
            "Signposting / Referral": "",
            "Eligibility Code": "X",
            "Gender": "M",
            "Case Costs": Decimal("99.5"),
            "Disbursements": Decimal("0"),
            "Disability Code": "ILL",
            "Suitable for Telephone Advice": "N",
            "Adjustments / Adaptations": "",
            "Date Closed": datetime.datetime(2014, 1, 2, 0, 0),
            "Age Range": "E",
            "Surname": "Corgi",
            "Account Number": "2B222B",
            "Postcode": "SW1A 1AA",
            "Ethnicity": "1",
            "Fixed Fee Amount": "LF",
            "Fixed Fee Code": "65",
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

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_is_2018_discrimination(self):
        for matter_type in contract_2018_category_spec["discrimination"]["MATTER_TYPE1"]:
            if get_applicable_contract(datetime.datetime(2019, 9, 1), matter_type) != CONTRACT_EIGHTEEN_DISCRIMINATION:
                self.fail("Applicable contract is not 2018 discrimination contract")

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_is_2018_education(self):
        for matter_type in contract_2018_category_spec["education"]["MATTER_TYPE1"]:
            if get_applicable_contract(datetime.datetime(2019, 9, 1), matter_type) != CONTRACT_EIGHTEEN_EDUCATION:
                self.fail("Applicable contract is not 2018 education contract")

    def test_invalid_field_count(self):
        validator = self.get_provider_csv_validator([[], []])
        with self.assertRaisesRegexp(serializers.ValidationError, r"Row: 1 - Incorrect number of columns"):
            validator.validate()

    def test_closed_date_after_opened_date_invariant(self):
        test_values = {
            "Matter Type 1": "EADM",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EB",
            "Outcome Code": "EB",
            "Date Opened": "02/01/2014",
            "Date Closed": "01/01/2014",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        with self.assertRaisesRegexp(serializers.ValidationError, "Row: 1 - .*must be after"):
            validator.validate()

    def test_invalid_account_number(self):
        test_values = {
            "Account Number": "22222B",
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EB",
            "Outcome Code": "EB",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        with self.assertRaises(serializers.ValidationError):
            validator.validate()

    def test_service_adapation_validation_valid(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EB",
            "Outcome Code": "EB",
            "Adjustments / Adaptations": "LOL",
        }
        data = [self._generate_contract_data_row(override=test_values)]
        validator = self.get_provider_csv_validator(data)
        with self.assertRaisesRegexp(serializers.ValidationError, r"Adjustments / Adaptations - LOL must be one of"):
            validator.validate()

    @override_settings(CONTRACT_2018_ENABLED=False)
    def test_allowed_no_outcome_code_and_dates_if_determination_code_2013(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Date Opened": "",
            "Date Closed": "",
            "Time Spent": "18",
            "Determination": "FINI",
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
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Date Opened": "",
            "Date Closed": "",
            "Fixed Fee Code": "NA",
            "Time Spent": "18",
            "Determination": "FINI",
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
        cleaned_data["Adjustments / Adaptations "] = ""
        with self.assertRaisesRegexp(serializers.ValidationError, r"Adjustments / Adaptations field is required"):
            validator._validate_service_adaptation(cleaned_data)

    @override_settings(CONTRACT_2018_ENABLED=False)
    def test_eligibility_code_validation_required(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Eligibility Code"] = ""
        with self.assertRaisesRegexp(serializers.ValidationError, r"Eligibility Code field is required"):
            validator._validate_eligibility_code_against_time_spent(cleaned_data)

    @override_settings(CONTRACT_2018_ENABLED=False)
    def test_validate_ta_oa_ff_not_valid_for_edu_and_dis(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Telephone / Online"] = "FF"
        validator._validate_telephone_or_online_advice(cleaned_data, "education")
        validator._validate_telephone_or_online_advice(cleaned_data, "discrimination")
        with self.assertRaisesRegexp(serializers.ValidationError, r".*code FF only valid for.*"):
            validator._validate_telephone_or_online_advice(cleaned_data, "ssss")

    @override_settings(CONTRACT_2018_ENABLED=False)
    def test_eligibility_code_validation_time_spent_less_than_132(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = "S"
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, r"The eligibility code .* you have entered is not valid"
        ):
            validator._validate_eligibility_code_against_time_spent(cleaned_data)

    @override_settings(CONTRACT_2018_ENABLED=False)
    def test_validation_time_spent_less_than_18(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = "S"
        cleaned_data["Determination"] = False
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, r"The eligibility code .* you have entered is not valid with"
        ):
            validator._validate_eligibility_code_against_time_spent(cleaned_data)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_eligibility_code_validation_required_2018(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Eligibility Code"] = ""
        with self.assertRaisesRegexp(serializers.ValidationError, r"Eligibility Code field is required"):
            validator._validate_eligibility_code_against_time_spent(cleaned_data)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validate_ta_oa_ff_not_valid_for_edu_and_dis_2018(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Telephone / Online"] = "FF"
        validator._validate_telephone_or_online_advice(cleaned_data, "education")
        validator._validate_telephone_or_online_advice(cleaned_data, "discrimination")
        with self.assertRaisesRegexp(serializers.ValidationError, r".*code FF only valid for.*"):
            validator._validate_telephone_or_online_advice(cleaned_data, "ssss")

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_eligibility_code_validation_time_spent_less_than_132_2018(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = "S"
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, r"The eligibility code .* you have entered is not valid"
        ):
            validator._validate_eligibility_code_against_time_spent(cleaned_data)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validation_time_spent_less_than_18_2018(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = "S"
        cleaned_data["Determination"] = False
        validator._validate_eligibility_code_against_time_spent(cleaned_data)
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, r"The eligibility code .* you have entered is not valid with"
        ):
            validator._validate_eligibility_code_against_time_spent(cleaned_data)

    def test_validation_time_spent_more_than_18_with_determination_not_valid(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Eligibility Code"] = "S"
        cleaned_data["Determination"] = True
        cleaned_data["Time Spent"] = 12
        validator._validate_time_spent(cleaned_data, "welfare")
        cleaned_data["Time Spent"] = 999
        with self.assertRaisesRegexp(
            serializers.ValidationError, "[u'Time spent (999) must not be greater than 42 minutes']"
        ):
            validator._validate_time_spent(cleaned_data, "discrimination")

        with self.assertRaisesRegexp(
            serializers.ValidationError, "[u'Time spent (999) must not be greater than 18 minutes']"
        ):
            validator._validate_time_spent(cleaned_data, "welfare")

        cleaned_data["Time Spent"] = 9
        with self.assertRaisesRegexp(serializers.ValidationError, "[u'Time spent (9) must be in 6 minute intervals']"):
            validator._validate_time_spent(cleaned_data, "welfare")

    def test_validation_exemption_code_or_cla_ref_required(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Date Opened"] = datetime.datetime(2014, 1, 1)
        cleaned_data["Exempted Code Reason"] = "aa"
        cleaned_data["Determination"] = False
        validator._validate_exemption(cleaned_data, "debt")
        cleaned_data["Date Opened"] = datetime.datetime(2014, 1, 2)

        with self.assertRaisesRegexp(
            serializers.ValidationError,
            "[u'An Exemption Reason can only be entered for Debt, Discrimination and Education matter]",
        ):
            validator._validate_exemption(cleaned_data, "welfare")

        cleaned_data["Exempted Code Reason"] = ""
        cleaned_data["CLA Reference Number"] = ""
        cleaned_data["Date Opened"] = datetime.datetime(2011, 1, 1)
        cleaned_data["Exceptional Cases (ref)"] = "foo"

        validator._validate_exemption(cleaned_data, "debt")
        cleaned_data["Exempted Code Reason"] = "aa"
        with self.assertRaisesRegexp(
            serializers.ValidationError,
            "[u'An Exemption Reason can only be entered for Debt, Discrimination and Education matter]",
        ):
            validator._validate_exemption(cleaned_data, "welfare")

    def test_category_consistency_validation(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Matter Type 1"] = "S"
        cleaned_data["Matter Type 2"] = "P"
        with self.assertRaisesRegexp(serializers.ValidationError, r"fields must be of the same category"):
            validator._validate_category_consistency(cleaned_data)

    def test_staged_reached_validate_required_mt1s(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Matter Type 1"] = "DMCA"
        cleaned_data["Stage Reached"] = ""
        with self.assertRaisesRegexp(
            serializers.ValidationError, r".*is required because Matter Type 1: DMCA was specified.*"
        ):
            validator._validate_stage_reached(cleaned_data)

    def test_staged_reached_validate_not_allowed_mt1s(self):
        validator = self.get_provider_csv_validator()
        cleaned_data = self.get_dummy_cleaned_data_copy()
        cleaned_data["Matter Type 1"] = "WBAA"
        with self.assertRaisesRegexp(
            serializers.ValidationError, r".*is not allowed because Matter Type 1: WBAA was specified.*"
        ):
            validator._validate_stage_reached(cleaned_data)

    def test_gte_validator(self):
        gte_0 = v.validate_gte(0)

        self.assertEqual(1, gte_0(1))
        with self.assertRaisesRegexp(serializers.ValidationError, ".*must be >= 0"):
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
            if expected_error not in e.detail:
                self.fail("{}".format(e))
        else:
            self.fail("Expected error missing: {}".format(expected_error))

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_debt_outcome_code_DAA_is_valid(self):
        test_values = {
            "Matter Type 1": "DPDE",
            "Matter Type 2": "DVAL",
            "Stage Reached": "DA",
            "Outcome Code": "DAA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_family_outcome_code_FAA_is_valid(self):
        test_values = {"Matter Type 1": "FAMA", "Matter Type 2": "FADV", "Outcome Code": "FAA"}
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_family_outcome_code_FAB_is_valid(self):
        test_values = {"Matter Type 1": "FAMA", "Matter Type 2": "FADV", "Outcome Code": "FAB"}
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_for_family_outcome_code_FAC_is_valid(self):
        test_values = {"Matter Type 1": "FAMA", "Matter Type 2": "FADV", "Outcome Code": "FAC"}
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_discrimination_outcome_code_QAA_is_valid(self):
        test_values = {
            "Matter Type 1": "QPRO",
            "Matter Type 2": "QAGE",
            "Stage Reached": "QA",
            "Outcome Code": "QAA",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_fafa_determination_code_is_valid(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EA",
            "Determination": "FAFA",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_exem_determination_code_is_valid(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EA",
            "Determination": "EXEM",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_housing_outcome_code_haa_is_valid(self):
        test_values = {
            "Matter Type 1": "HRNT",
            "Matter Type 2": "HPRI",
            "Stage Reached": "HA",
            "Outcome Code": "HAA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_housing_outcome_code_hac_is_valid(self):
        test_values = {
            "Matter Type 1": "HRNT",
            "Matter Type 2": "HPRI",
            "Stage Reached": "HA",
            "Outcome Code": "HAC",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_housing_outcome_code_hab_is_valid(self):
        test_values = {
            "Matter Type 1": "HRNT",
            "Matter Type 2": "HPRI",
            "Stage Reached": "HA",
            "Outcome Code": "HAB",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_education_outcome_code_eaa_is_valid(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EA",
            "Outcome Code": "EAA",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_education_matter_type1_code_edjr_is_valid(self):
        test_values = {
            "Matter Type 1": "EDJR",
            "Matter Type 2": "ENUR",
            "Stage Reached": "EA",
            "Outcome Code": "EZ",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_invalid_outcome_code(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EA",
            "Outcome Code": "INVALID",
            "Fixed Fee Code": "NA",
        }
        expected_error = "Row: 1 - You have not selected a valid Outcome Code."
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_fixed_fee_amount_present(self):
        test_values = {
            "Matter Type 1": "DMAP",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "130",
            "Fixed Fee Code": "LF",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_fixed_fee_amount_missing(self):
        test_values = {
            "Matter Type 1": "DMAP",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "",
            "Fixed Fee Code": "HF",
        }
        expected_error = "Row: 1 - Fixed Fee Amount must be entered for Fixed Fee Code (HF)"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_lower_fixed_fee_time_spent(self):
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "65",
            "Fixed Fee Code": "LF",
            "Time Spent": "132",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_lower_fixed_fee_excess_time_spent(self):
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "65",
            "Fixed Fee Code": "LF",
            "Time Spent": "133",
        }
        expected_error = "Row: 1 - The Fixed Fee code you have entered is not valid with time spent on the case"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_higher_fixed_fee_time_spent_bounds(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "DMAP",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "130",
            "Fixed Fee Code": "HF",
        }
        lower_bound = "133"
        upper_bound = "899"
        for time_spent in [lower_bound, upper_bound]:
            test_values["Time Spent"] = time_spent
            self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_higher_fixed_fee_excess_time_spent(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "DMAP",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "130",
            "Fixed Fee Code": "HF",
            "Time Spent": "900",
        }
        expected_error = "Row: 1 - The Fixed Fee code you have entered is not valid with time spent on the case"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_higher_fixed_fee_insufficient_time_spent(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "DMAP",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "130",
            "Fixed Fee Code": "HF",
            "Time Spent": "132",
        }
        expected_error = "Row: 1 - The Fixed Fee code you have entered is not valid with time spent on the case"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_hourly_rate_fixed_fee_time_spent(self):
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Code": "HR",
            "Time Spent": "900",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_hourly_rate_fixed_fee_insufficient_time_spent(self):
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Code": "HR",
            "Time Spent": "899",
        }
        expected_error = "Row: 1 - The Fixed Fee code you have entered is not valid with time spent on the case"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_fixed_fee_code_df_is_valid(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "HRNT",
            "Matter Type 2": "HPRI",
            "Stage Reached": "HA",
            "Fixed Fee Code": "DF",
            "Fixed Fee Amount": "40.0",
            "Determination": "FINI",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_df_fixed_fee_amount_is_valid(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "HRNT",
            "Matter Type 2": "HPRI",
            "Stage Reached": "HA",
            "Fixed Fee Code": "DF",
            "Determination": "FINI",
        }
        valid_amounts = [0, 0.50, 10, 20.50, 40]
        for amount in valid_amounts:
            test_values["Fixed Fee Amount"] = "{}".format(amount)
            self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_df_fixed_fee_amount_invalid(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "HRNT",
            "Matter Type 2": "HPRI",
            "Stage Reached": "HA",
            "Fixed Fee Code": "DF",
            "Determination": "FINI",
        }
        invalid_amounts = [40.01, 100]
        for amount in invalid_amounts:
            test_values["Fixed Fee Amount"] = "{}".format(amount)
            expected_error = "Row: 1 - The value you have entered exceeds the Fixed Fee"
            self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_df_fixed_fee_negative_amount_fails(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "HRNT",
            "Matter Type 2": "HPRI",
            "Stage Reached": "HA",
            "Fixed Fee Code": "DF",
            "Fixed Fee Amount": "-1",
            "Determination": "FINI",
        }
        expected_error = "Row: 1 Field (20 / T): Fixed Fee Amount - Field must be >= 0"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    # TODO enable when Matter Type 1 MSCB added
    # @override_settings(CONTRACT_2018_ENABLED=True)
    # def test_validator_misc_rate_fixed_fee(self):
    #     test_values = {"Matter Type 1": u"MSCB", "Fixed Fee Amount": u"", "Fixed Fee Code": u"MR"}
    #     self._test_generated_2018_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_hwfm_rate_fixed_fee(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "FAMY",
            "Matter Type 2": "FMEC",
            "Fixed Fee Amount": "119.6",
            "Fixed Fee Code": "HM",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_hwfm_rate_fixed_fee_mt1_incorrect(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "FAMZ",
            "Matter Type 2": "FMEC",
            "Fixed Fee Amount": "119.6",
            "Fixed Fee Code": "HM",
        }
        expected_error = (
            "Row: 1 - The Fixed Fee code you have entered is not valid with the Matter Type 1 Code entered"
        )
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_validator_mt1_fixed_fee_code_mismatch(self):
        test_values = {
            "Matter Type 1": "FAMY",
            "Matter Type 2": "FMEC",
            "Fixed Fee Amount": "119.6",
            "Fixed Fee Code": "LF",
        }
        expected_error = "Row: 1 - The HM fee code should be used where Matter Type 1 Code - FAMY is used"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_hourly_rate_hr_fixed_fee_code(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "DMAP",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "119.6",
            "Fixed Fee Code": "HR",
            "Time Spent": "900",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_eligibility_codes_with_lf_fixed_fee(self):
        lf_eligibility_codes = {"S", "T", "V", "W", "X", "Z"}
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Code": "LF",
        }
        for eligibility_code in lf_eligibility_codes:
            test_values["Eligibility Code"] = eligibility_code
            self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_eligibility_codes_missing_lf_fixed_fee(self):
        lf_eligibility_codes = {"S", "W", "X", "Z"}
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "65",
            "Fixed Fee Code": "HF",
            "Time Spent": "133",
        }
        for eligibility_code in lf_eligibility_codes:
            test_values["Eligibility Code"] = eligibility_code
            expected_error = (
                "Row: 1 - The Fixed Fee code you have entered is not valid with the Eligibility Code entered"
            )
            self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_eligibility_codes_with_hf_fixed_fee(self):
        hf_eligibility_codes = {"T", "V"}
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Code": "HF",
            "Time Spent": "133",
        }
        for eligibility_code in hf_eligibility_codes:
            test_values["Eligibility Code"] = eligibility_code
            self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_eligibility_codes_missing_hf_fixed_fee(self):
        lf_eligibility_codes = {"S", "W", "X", "Z"}
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Amount": "65",
            "Fixed Fee Code": "HF",
            "Time Spent": "133",
        }
        for eligibility_code in lf_eligibility_codes:
            test_values["Eligibility Code"] = eligibility_code
            expected_error = (
                "Row: 1 - The Fixed Fee code you have entered is not valid with the Eligibility Code entered"
            )
            self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_fixed_fee_invalid_error_message(self):
        test_values = {
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Code": "NA",
            "Time Spent": "133",
        }
        expected_error = "Row: 1 - The Fixed Fee code you have entered is not valid for this case"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_discrimination_eligibility_codes(self):
        code = "S"
        time = "135"
        test_values = {
            "Matter Type 1": "QPRO",
            "Matter Type 2": "QAGE",
            "Stage Reached": "QA",
            "Fixed Fee Code": "NA",
            "Eligibility Code": code,
            "Time Spent": time,
        }
        expected_error = "Row: 1 - The eligibility code ({code}) you have entered is not valid with the time spent ({time}) on this case, please review the eligibility code.".format(
            code=code, time=time
        )
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_education_eligibility_codes(self):
        code = "Z"
        time = "135"
        test_values = {
            "Matter Type 1": "ESEN",
            "Matter Type 2": "ECOL",
            "Stage Reached": "ED",
            "Fixed Fee Code": "NA",
            "Eligibility Code": code,
            "Time Spent": time,
        }
        expected_error = "Row: 1 - The eligibility code ({code}) you have entered is not valid with the time spent ({time}) on this case, please review the eligibility code.".format(
            code=code, time=time
        )
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_discrimination_fixed_fee_invalid_error_message(self):
        test_values = {
            "Matter Type 1": "HHOM",
            "Matter Type 2": "HHLS",
            "Stage Reached": "HB",
            "Fixed Fee Amount": "130",
            "Fixed Fee Code": "HF",
            "Time Spent": "90",
            "Date Opened": "24/07/2018",
            "Date Closed": "17/01/2019",
        }
        expected_error = "Row: 1 - Fixed Fee Code NA must be entered for 2013 cases (pre-01/09/18), 2018 Discrimination cases or 2018 Education cases"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_education_fixed_fee_invalid_error_message(self):
        test_values = {
            "Matter Type 1": "ESEN",
            "Matter Type 2": "ENUR",
            "Stage Reached": "EA",
            "Fixed Fee Amount": "130",
            "Fixed Fee Code": "HF",
            "Time Spent": "90",
            "Date Opened": "24/09/2018",
            "Date Closed": "17/01/2019",
        }
        expected_error = "Row: 1 - Fixed Fee Code NA must be entered for 2013 cases (pre-01/09/18), 2018 Discrimination cases or 2018 Education cases"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_signposting_code(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EA",
            "Signposting / Referral": "OOSC",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_signposting_lrep_code(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EA",
            "Signposting / Referral": "LREP",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_signposting_code_invalid(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EA",
            "Signposting / Referral": "FOO",
            "Fixed Fee Code": "NA",
        }
        expected_error = (
            "Row: 1 - The Signposting / Referral code you have entered is invalid. Please enter a valid code."
        )
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_signposting_code_present_for_outcome_codes(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EB",
            "Outcome Code": "EU",
            "Signposting / Referral": "OOSC",
            "Fixed Fee Code": "NA",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_signposting_code_missing_for_outcome_codes(self):
        test_values = {
            "Matter Type 1": "EPRO",
            "Matter Type 2": "ESOS",
            "Stage Reached": "EB",
            "Outcome Code": "EV",
            "Signposting / Referral": "",
        }
        expected_error = (
            "Row: 1 - A Signposting / Referral reason code must be entered for matters with outcome code EV."
        )
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_df_fixed_fee_has_determination_code(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Fixed Fee Code": "DF",
            "Fixed Fee Amount": "40.0",
            "Determination": "FINI",
        }
        self._test_generated_contract_row_validates(override=test_values)

    @override_settings(CONTRACT_2018_ENABLED=True)
    def test_df_fixed_fee_missing_determination_code(self):
        test_values = {
            "Eligibility Code": "V",
            "Matter Type 1": "DTOT",
            "Matter Type 2": "DOTH",
            "Stage Reached": "DB",
            "Fixed Fee Code": "DF",
        }
        expected_error = "Row: 1 - The Fixed Fee code you have entered is not valid with Determination Code entered"
        self._test_generated_2018_contract_row_validate_fails(override=test_values, expected_error=expected_error)


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
