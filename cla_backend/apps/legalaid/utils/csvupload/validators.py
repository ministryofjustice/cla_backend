import datetime
import logging
import re
import types
from collections import OrderedDict
from copy import deepcopy
from decimal import Decimal, InvalidOperation

from django.forms.util import ErrorList
from rest_framework import serializers

from legalaid.utils.csvupload.constants import (
    AGE_RANGE,
    POSTCODE_RE,
    ELIGIBILITY_CODES,
    DISABILITY_INDICATOR,
    EXEMPTION_CODES,
    SERVICE_ADAPTATIONS,
    ADVICE_TYPES,
    PREFIX_CATEGORY_LOOKUP,
    STAGE_REACHED_NOT_ALLOWED_MT1S,
    STAGE_REACHED_REQUIRED_MT1S,
)
from legalaid.utils.csvupload.contracts import (
    get_applicable_contract,
    get_determination_codes,
    get_valid_outcomes,
    get_valid_matter_type1,
    get_valid_matter_type2,
    get_valid_stage_reached,
    contract_2018_fixed_fee_codes,
    CONTRACT_THIRTEEN,
    CONTRACT_EIGHTEEN,
)

logger = logging.getLogger(__name__)
date_pattern = re.compile("^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$")


def validate_decimal(val):
    if val:
        try:
            val = val.replace(u",", u"")
            val = Decimal(val)
            return val
        except (ValueError, InvalidOperation) as ve:
            raise serializers.ValidationError(str(ve))


def validate_integer(val):
    if val:
        try:
            val = int(val)
            return val
        except ValueError as ve:
            raise serializers.ValidationError(str(ve))


def validate_gte(minimum):
    minimum = minimum

    def _validate_gte(val):
        if val and (val < minimum):
            raise serializers.ValidationError("Field must be > %s" % minimum)
        return val

    return _validate_gte


def validate_present(val, message=None):
    message = message or "is required"
    if not val:
        raise serializers.ValidationError(message)
    return val


def validate_date(val):
    val = val.strip()
    if val:
        try:
            assert date_pattern.match(val)
            day, month, year = val.split("/")
            return datetime.datetime(int(year), int(month), int(day))
        except (ValueError, TypeError, AssertionError):
            raise serializers.ValidationError("%s is not a valid date (DD/MM/YYYY)" % val)


def validate_not_present(val, message=None):
    message = message or "Field should not be present"
    if val.strip():
        raise serializers.ValidationError(message)
    return val


def validate_not_current_month(val):
    if val:
        now = datetime.datetime.now().replace(day=1).date()
        val_month = val.replace(day=1).date()
        if now == val_month:
            raise serializers.ValidationError("Date (%s) must not be from current month" % val.date())
    return val


def validate_regex(regex, flags=None):
    compiled_re = re.compile(regex, flags)

    def _validate_regex(val):
        if val and (not compiled_re.match(val)):
            raise serializers.ValidationError("Field value (%s) doesn't match pattern: %s" % (val, regex))
        return val

    return _validate_regex


validate_postcode = validate_regex(POSTCODE_RE, flags=re.VERBOSE | re.I)


def validate_in(iterable):
    def _validate_in(val):
        if val and (val not in iterable):
            raise serializers.ValidationError("%s must be one of %s" % (val, ", ".join(iterable)))
        return val

    return _validate_in


def inverted_reduce(x, f):
    return f(x)


def value_is_truthy(x):
    return bool(x)


def value_is_falsey(x):
    return not bool(x)


def value_not_equal(x):
    return lambda y: x != y


def value_is_date_after_apr_2013(x):
    return x and x > datetime.datetime(2013, 4, 1)


class depends_on(object):
    """
    A decorator to run a function if and only if the
    second arg passed to that function contains a key
    that passes a check.

    >>> d = {'a': True}
    >>> class A(object):
    >>>     @depends_on('a', check=value_is_truthy)
    >>>     def do_something(self, d):
    >>>         return 1

    The above will only run if a in dict d is passes the check 'TRUTHY'

    This can be improved to be more generic by supporting plain functions and
    instance methods, also allowing user to specify the arg or kwarg to expect
    a dict instead of hard coding args[1]

    """

    def __init__(self, depends_field, check=None):
        self.depends_field = depends_field
        if not check:
            self.check = value_is_truthy
        else:
            self.check = check

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            assert isinstance(args[1], types.DictType)
            if self.check(args[1].get(self.depends_field)):
                return f(*args, **kwargs)

        return wrapped_f


def excel_col_name(col):  # col is 1 based
    excel_col = ""
    div = col
    while div:
        (div, mod) = divmod(div - 1, 26)  # will return (x, 0 .. 25)
        excel_col = chr(mod + 65) + excel_col
    return excel_col


account_number_regex_validator = validate_regex(r"\d{1}[a-z]{1}\d{3}[a-z]{1}", flags=re.IGNORECASE)

contract_2013_field_order = [
    "CLA Reference Number",
    "Client Ref",
    "Account Number",
    "First Name",
    "Surname",
    "DOB",
    "Age Range",
    "Gender",
    "Ethnicity",
    "Unused1",
    "Unused2",
    "Postcode",
    "Eligibility Code",
    "Matter Type 1",
    "Matter Type 2",
    "Stage Reached",
    "Outcome Code",
    "Unused3",
    "Date Opened",
    "Date Closed",
    "Time Spent",
    "Case Costs",
    "Unused4",
    "Disability Code",
    "Disbursements",
    "Travel Costs",
    "Determination",
    "Suitable for Telephone Advice",
    "Exceptional Cases (ref)",
    "Exempted Reason Code",
    "Adjustments / Adaptations",
    "Signposting / Referral",
    "Media Code",
    "Telephone / Online",
]

validators = {
    "CLA Reference Number": [validate_present, validate_integer],
    "Client Ref": [validate_present],
    "Account Number": [validate_present, account_number_regex_validator],
    "First Name": [validate_present],
    "Surname": [validate_present],
    "DOB": [validate_date],
    "Age Range": [validate_present, validate_in(AGE_RANGE)],
    "Gender": [validate_present],
    "Ethnicity": [validate_present],
    "Unused1": [validate_not_present],
    "Unused2": [validate_not_present],
    "Postcode": [validate_present, validate_postcode],
    "Eligibility Code": [validate_in(ELIGIBILITY_CODES)],
    "Matter Type 1": [validate_present, validate_in(get_valid_matter_type1(CONTRACT_THIRTEEN))],
    "Matter Type 2": [validate_present, validate_in(get_valid_matter_type2(CONTRACT_THIRTEEN))],
    "Stage Reached": [validate_in(get_valid_stage_reached(CONTRACT_THIRTEEN))],
    "Outcome Code": [validate_in(get_valid_outcomes(CONTRACT_THIRTEEN))],
    "Unused3": [validate_not_present],
    "Date Opened": [validate_date],
    "Date Closed": [validate_date, validate_not_current_month],
    "Time Spent": [validate_present, validate_integer, validate_gte(0)],
    "Case Costs": [validate_present, validate_decimal],
    "Unused4": [validate_not_present],
    "Disability Code": [validate_present, validate_in(DISABILITY_INDICATOR)],
    "Disbursements": [validate_decimal],
    "Travel Costs": [validate_decimal],
    "Determination": [validate_in(get_determination_codes(CONTRACT_THIRTEEN))],
    "Suitable for Telephone Advice": [validate_in({u"Y", u"N"})],
    "Exceptional Cases (ref)": [validate_regex(r"\d{7}[a-z]{2}", re.I)],
    "Exempted Reason Code": [validate_in(EXEMPTION_CODES)],
    "Adjustments / Adaptations": [validate_in(SERVICE_ADAPTATIONS)],
    "Signposting / Referral": [],
    "Media Code": [],
    "Telephone / Online": [validate_present, validate_in(ADVICE_TYPES)],
}

contract_2013_validators = OrderedDict()
for field in contract_2013_field_order:
    contract_2013_validators[field] = deepcopy(validators[field])

contract_2018_field_order = [
    "CLA Reference Number",
    "Client Ref",
    "Account Number",
    "First Name",
    "Surname",
    "DOB",
    "Age Range",
    "Gender",
    "Ethnicity",
    "Unused1",
    "Unused2",
    "Postcode",
    "Eligibility Code",
    "Matter Type 1",
    "Matter Type 2",
    "Stage Reached",
    "Outcome Code",
    "Unused3",
    "Date Opened",
    "Date Closed",
    "Time Spent",
    "Case Costs",
    "Fixed Fee Amount",
    "Fixed Fee Code",
    "Disability Code",
    "Disbursements",
    "Travel Costs",
    "Determination",
    "Suitable for Telephone Advice",
    "Exceptional Cases (ref)",
    "Exempted Reason Code",
    "Adjustments / Adaptations",
    "Signposting / Referral",
    "Media Code",
    "Telephone / Online",
]

validators.update(
    {
        "Matter Type 1": [validate_present, validate_in(get_valid_matter_type1(CONTRACT_EIGHTEEN))],
        "Matter Type 2": [validate_present, validate_in(get_valid_matter_type2(CONTRACT_EIGHTEEN))],
        "Stage Reached": [validate_in(get_valid_stage_reached(CONTRACT_EIGHTEEN))],
        "Outcome Code": [validate_in(get_valid_outcomes(CONTRACT_EIGHTEEN))],
        "Determination": [validate_in(get_determination_codes(CONTRACT_EIGHTEEN))],
        "Fixed Fee Amount": [],
        "Fixed Fee Code": [validate_in(contract_2018_fixed_fee_codes)],
    }
)

contract_2018_validators = OrderedDict()
for field in contract_2018_field_order:
    contract_2018_validators[field] = deepcopy(validators[field])

date_opened_index = [i for i, key in enumerate(contract_2013_validators) if key == "Date Opened"][0]


class ProviderCSVValidator(object):
    def __init__(self, rows):
        self.rows = rows
        self.cleaned_data = []

    def _validate_field(self, field_name, field_value, idx, row_num, validators):
        # Field Validation
        try:
            # reduce the validators over the original field value, save
            # the final value into self.cleaned_data[field_name]
            cleaned_value = reduce(inverted_reduce, validators, field_value)

            return cleaned_value

        except serializers.ValidationError as ve:
            ve.message = "Row: %s Field (%s / %s): %s - %s" % (
                row_num + 1,
                idx + 1,
                excel_col_name(idx + 1),
                field_name,
                ve.message,
            )
            raise ve

    @staticmethod
    def _get_applicable_contract_for_row(row):
        try:
            case_date_opened_string = row[date_opened_index]
            case_date_opened = validate_date(case_date_opened_string)
            return get_applicable_contract(case_date_opened=case_date_opened)  # TODO pass Matter Type 1
        except IndexError:
            logger.warning("Could not get applicable contract for row, defaulting to 2013. \nRow: {}".format(row))
            return CONTRACT_THIRTEEN

    def _get_validators_for_row(self, row):
        applicable_contract = self._get_applicable_contract_for_row(row)
        if applicable_contract == CONTRACT_THIRTEEN:
            return contract_2013_validators
        elif applicable_contract == CONTRACT_EIGHTEEN:
            return contract_2018_validators

    def _validate_fields(self):
        """
        Validate individual field values, like django's clean_<fieldname> with
        less magic ( no setattr('clean_'+field_name) junk) just loop over
        the fields and apply the validators specified in the
        field spec (self._get_expected_fields_for_row(row))
        """
        cleaned_data = {}
        errors = ErrorList()

        for row_num, row in enumerate(self.rows):
            expected_fields = self._get_validators_for_row(row)
            if len(row) != len(expected_fields):
                raise serializers.ValidationError(
                    "Row: %s - Incorrect number of columns should be %s "
                    "actually %s" % (row_num + 1, len(expected_fields), len(row))
                )

            for idx, field_name in enumerate(expected_fields):
                field_value = row[idx]
                validators = expected_fields[field_name]
                try:
                    cleaned_data[field_name] = self._validate_field(
                        field_name, field_value.strip(), idx, row_num, validators
                    )
                except serializers.ValidationError as ve:
                    errors.append(ve)
                except (AssertionError, TypeError) as e:
                    errors.append(e)
            try:
                # Global Validation
                applicable_contract = self._get_applicable_contract_for_row(row)
                self.cleaned_data.append(self._validate_data(cleaned_data, row_num, applicable_contract))
            except serializers.ValidationError as ve:
                errors.extend(ve.error_list)

        if len(errors):
            raise serializers.ValidationError(errors)

    @staticmethod
    def _validate_open_closed_date(cleaned_data):
        opened = cleaned_data.get("Date Opened")
        closed = cleaned_data.get("Date Closed")
        today = datetime.date.today()
        if closed and not opened:
            raise serializers.ValidationError("If you have Closed date you " "must also have an Opened date")
        if opened and closed:
            if closed < datetime.datetime(2013, 4, 1):
                raise serializers.ValidationError("Closed date must be after 01/04/2013")
            if closed.month == today.month and closed.year == today.year:
                raise serializers.ValidationError("Closed date must not be in the current month")
            if closed < opened:
                raise serializers.ValidationError(
                    "Closed date (%s) must be after opened date (%s)"
                    % (closed.date().isoformat(), opened.date().isoformat())
                )

    @depends_on("Determination", check=value_is_falsey)
    @depends_on("Date Opened", check=value_is_date_after_apr_2013)
    def _validate_service_adaptation(self, cleaned_data):
        validate_present(
            cleaned_data.get("Adjustments / Adaptations"), message="Adjustments / Adaptations field is required"
        )

    @depends_on("Determination", check=value_is_falsey)
    def _validate_media_code(self, cleaned_data):
        validate_present(
            cleaned_data.get("Media Code"), message="Media Code is required because no determination was specified"
        )

    @depends_on("Determination", check=value_is_falsey)
    def _validate_eligibility_code(self, cleaned_data):
        code = cleaned_data.get("Eligibility Code")
        time_spent = cleaned_data.get("Time Spent", 0)
        validate_present(code, message="Eligibility Code field is required because no determination was specified")
        # check time spent
        if code in {u"S", u"W", u"X", u"Z"} and time_spent > 132:
            raise serializers.ValidationError(
                u"The eligibility code (%s) you have entered is not valid with "
                u"the time spent (%s) on this case, please review the "
                u"eligibility code." % (code, time_spent)
            )

    @staticmethod
    def _validate_category_consistency(cleaned_data):
        mt1, mt2, outcome, stage = (
            cleaned_data.get("Matter Type 1"),
            cleaned_data.get("Matter Type 2"),
            cleaned_data.get("Outcome Code"),
            cleaned_data.get("Stage Reached"),
        )

        category_dependent_fields = [mt1, mt2, outcome, stage]
        prefixes = {x[0] for x in category_dependent_fields if x}
        if not len(prefixes) == 1:
            raise serializers.ValidationError(
                "Matter Type 1 (%s), Matter Type 2 (%s), Outcome Code (%s) "
                "and Stage Reached (%s) fields must be of the same category." % (mt1, mt2, outcome, stage)
            )

        return PREFIX_CATEGORY_LOOKUP[list(prefixes)[0]]

    @depends_on("Age Range", check=value_not_equal(u"U"))
    def _validate_dob_present(self, cleaned_data):
        validate_present(cleaned_data.get("DOB"), "A date of birth is required unless" " Age range is set to 'U'")

    @depends_on("Determination", check=value_is_truthy)
    def _validate_time_spent(self, cleaned_data, category):
        MAX_TIME_ALLOWED = 18
        if category == u"discrimination":
            MAX_TIME_ALLOWED = 42

        time_spent_in_minutes = cleaned_data.get("Time Spent", 0)
        if time_spent_in_minutes > MAX_TIME_ALLOWED:
            raise serializers.ValidationError(
                "Time spent (%s) must not be greater than %s minutes" % (time_spent_in_minutes, MAX_TIME_ALLOWED)
            )
        if time_spent_in_minutes % 6:
            raise serializers.ValidationError("Time spent (%s) must be in 6 minute intervals" % time_spent_in_minutes)

    @depends_on("Exempted Code Reason", check=value_is_truthy)
    @depends_on("Determination", check=value_is_falsey)
    def _validate_exemption(self, cleaned_data, category):
        exempt_categories = {u"debt", u"discrimination", u"education"}
        if cleaned_data.get("Date Opened") > datetime.datetime(2013, 4, 1) and category in exempt_categories:
            validate_present(
                cleaned_data.get("Exempted Code Reason", cleaned_data.get("CLA Reference Number")),
                message="Exempt Code Reason or CLA Reference number required before case was opened after 1st Apr 2013",
            )

        if category not in exempt_categories:
            raise serializers.ValidationError(
                "An Exemption Reason can only be entered for Debt, " "Discrimination and Education matters"
            )

    def _validate_telephone_or_online_advice(self, cleaned_data, category):
        ta = cleaned_data.get("Telephone / Online")
        if category not in {u"education", u"discrimination"} and ta == u"FF":
            raise serializers.ValidationError(
                "code FF only valid for Telephone Advice/Online Advice field if "
                "category is Education or Discrimination"
            )

    @depends_on("Determination", check=value_is_falsey)
    def _validate_stage_reached(self, cleaned_data):
        mt1 = cleaned_data.get("Matter Type 1")
        stage_reached_code = cleaned_data.get("Stage Reached")

        if mt1 in STAGE_REACHED_REQUIRED_MT1S:
            validate_present(
                stage_reached_code,
                message='Field "Stage Reached" is required because Matter Type 1: %s was specified' % mt1,
            )
        if mt1 in STAGE_REACHED_NOT_ALLOWED_MT1S:
            validate_not_present(
                stage_reached_code,
                message='Field "Stage Reached" is not allowed because Matter Type 1: %s was specified' % mt1,
            )

    @depends_on("Determination", check=value_is_truthy)
    def _validate_determination_dvca_is_family(self, cleaned_data, category):
        determination = cleaned_data.get("Determination")
        if determination == u"DVCA" and category != u"family":
            raise serializers.ValidationError("Category (%s) must be Family if Determination is DVCA" % category)

    def _validate_fixed_fee_amount_present(self, cleaned_data):
        fixed_fee_code = cleaned_data.get("Fixed Fee Code")
        if fixed_fee_code in ["DF", "LF", "HF"]:
            if not cleaned_data.get("Fixed Fee Amount"):
                raise serializers.ValidationError(
                    "Fixed Fee Amount must be entered for Fixed Fee Code ({})".format(fixed_fee_code)
                )

    def _validate_lower_fixed_fee_time_spent(self, cleaned_data):
        MAX_TIME_ALLOWED = 133
        time_spent_in_minutes = cleaned_data.get("Time Spent", 0)
        fixed_fee_code = cleaned_data.get("Fixed Fee Code")
        if fixed_fee_code == "LF" and time_spent_in_minutes >= MAX_TIME_ALLOWED:
            raise serializers.ValidationError(
                "Time spent must be less than {} minutes for LF fixed fee code".format(MAX_TIME_ALLOWED)
            )

    @staticmethod
    def format_message(s, row_num):
        return "Row: %s - %s" % (row_num + 1, s)

    def _validate_data(self, cleaned_data, row_num, applicable_contract):
        """
        Like django's clean method, use this to validate across fields
        """

        errors = ErrorList()

        validation_methods = [
            self._validate_open_closed_date,
            self._validate_service_adaptation,
            self._validate_media_code,
            self._validate_eligibility_code,
            self._validate_stage_reached,
            self._validate_dob_present,
        ]
        if applicable_contract == CONTRACT_EIGHTEEN:
            validation_methods.extend(
                [self._validate_fixed_fee_amount_present, self._validate_lower_fixed_fee_time_spent]
            )

        validation_methods_depend_on_category = [
            self._validate_time_spent,
            self._validate_exemption,
            self._validate_telephone_or_online_advice,
            self._validate_determination_dvca_is_family,
        ]

        for m in validation_methods:
            try:
                m(cleaned_data)
            except serializers.ValidationError as ve:
                errors.append(self.format_message(ve.message, row_num))
        try:
            category = self._validate_category_consistency(cleaned_data)
        except serializers.ValidationError as ve:
            errors.append(self.format_message(ve.message, row_num))
            raise serializers.ValidationError(errors)

        for m in validation_methods_depend_on_category:
            try:
                m(cleaned_data, category)
            except serializers.ValidationError as ve:
                errors.append(self.format_message(ve.message, row_num))

        if len(errors):
            raise serializers.ValidationError(errors)

        return cleaned_data

    def validate(self):
        self._validate_fields()
        return self.cleaned_data
