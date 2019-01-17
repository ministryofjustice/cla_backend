import datetime
from decimal import Decimal, InvalidOperation
import types
import re

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
    get_determination_codes,
    get_valid_outcomes,
    get_valid_matter_type1,
    get_valid_matter_type2,
    get_valid_stage_reached,
    PREFIX_CATEGORY_LOOKUP,
    STAGE_REACHED_NOT_ALLOWED_MT1S,
    STAGE_REACHED_REQUIRED_MT1S,
)

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


TRUTHY = lambda x: bool(x)  # noqa: E731
FALSEY = lambda x: not bool(x)  # noqa: E731
NOT_EQUAL = lambda y: lambda x: x != y  # noqa: E731
AFTER_APR_2013 = lambda x: x and x > datetime.datetime(2013, 4, 1)  # noqa: E731


class depends_on(object):
    """
    A decorator to run a function if and only if the
    second arg passed to that function contains a key
    that passes a check.

    >>> d = {'a': True}
    >>> class A(object):
    >>>     @depends_on('a', check=TRUTHY)
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
            self.check = TRUTHY
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


class ProviderCSVValidator(object):
    def __init__(self, rows):
        self.rows = rows
        self.cleaned_data = []
        # the index is the offset in the csv
        self.fields = (
            # 'name', iterable of validators to apply
            ("CLA Reference Number", [validate_present, validate_integer]),  # 1
            ("Client Ref", [validate_present]),  # 2
            (
                "Account Number",
                [validate_present, validate_regex(r"\d{1}[a-z]{1}\d{3}[a-z]{1}", flags=re.IGNORECASE)],
            ),  # 3
            ("First Name", [validate_present]),  # 4
            ("Surname", [validate_present]),  # 5
            ("DOB", [validate_date]),  # 6
            ("Age Range", [validate_present, validate_in(AGE_RANGE)]),  # 7
            ("Gender", [validate_present]),  # 8
            ("Ethnicity", [validate_present]),  # 9
            ("Unused1", [validate_not_present]),  # 10
            ("Unused2", [validate_not_present]),  # 11
            ("Postcode", [validate_present, validate_postcode]),
            # 12
            ("Eligibility Code", [validate_in(ELIGIBILITY_CODES)]),  # 13
            ("Matter Type 1", [validate_present, validate_in(get_valid_matter_type1())]),
            # 14
            ("Matter Type 2", [validate_present, validate_in(get_valid_matter_type2())]),
            # 15
            ("Stage Reached", [validate_in(get_valid_stage_reached())]),  # 16
            ("Outcome Code", [validate_in(get_valid_outcomes())]),  # 17
            ("Unused3", [validate_not_present]),  # 18
            ("Date Opened", [validate_date]),  # 19
            ("Date Closed", [validate_date, validate_not_current_month]),  # 20
            ("Time Spent", [validate_present, validate_integer, validate_gte(0)]),  # 21
            ("Case Costs", [validate_present, validate_decimal]),  # 22
            ("Unused4", [validate_not_present]),  # 23
            ("Disability Code", [validate_present, validate_in(DISABILITY_INDICATOR)]),  # 24
            ("Disbursements", [validate_decimal]),  # 25
            ("Travel Costs", [validate_decimal]),  # 26
            ("Determination", [validate_in(get_determination_codes())]),  # 27
            ("Suitable for Telephone Advice", [validate_in({u"Y", u"N"})]),  # 28
            ("Exceptional Cases (ref)", [validate_regex(r"\d{7}[a-z]{2}", re.I)]),
            # 29
            ("Exempted Reason Code", [validate_in(EXEMPTION_CODES)]),  # 30
            ("Adjustments / Adaptations", [validate_in(SERVICE_ADAPTATIONS)]),  # 31
            ("Signposting / Referral", []),  # 32
            ("Media Code", []),
            # 33 TODO: Maybe put [validate_present]) back depending on reply from Alex A.
            ("Telephone / Online", [validate_present, validate_in(ADVICE_TYPES)]),
            # 34
        )

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

    def _validate_fields(self):
        """
        Validate individual field values, like django's clean_<fieldname> with
        less magic ( no setattr('clean_'+field_name) junk) just loop over
        the fields and apply the validators specified in the
        field spec (self.fields)
        """
        cleaned_data = {}
        errors = ErrorList()

        for row_num, row in enumerate(self.rows):
            if len(row) != len(self.fields):
                raise serializers.ValidationError(
                    "Row: %s - Incorrect number of columns should be %s "
                    "actually %s" % (row_num + 1, len(self.fields), len(row))
                )

            for idx, field_value in enumerate(row):
                field_name, validators = self.fields[idx]
                try:
                    cleaned_data[field_name] = self._validate_field(
                        field_name, field_value.strip(), idx, row_num, validators
                    )
                except serializers.ValidationError as ve:
                    errors.append(ve)
            try:
                # Global Validation
                self.cleaned_data.append(self._validate_data(cleaned_data, row_num))
            except serializers.ValidationError as ve:
                errors.extend(ve.error_list)

        if len(errors):
            raise serializers.ValidationError(errors)

    def _validate_open_closed_date(self, cleaned_data):
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

    @depends_on("Determination", check=FALSEY)
    @depends_on("Date Opened", check=AFTER_APR_2013)
    def _validate_service_adaptation(self, cleaned_data):
        validate_present(
            cleaned_data.get("Adjustments / Adaptations"), message="Adjustments / Adaptations field is required"
        )

    @depends_on("Determination", check=FALSEY)
    def _validate_media_code(self, cleaned_data):
        validate_present(
            cleaned_data.get("Media Code"), message="Media Code is required because no determination was specified"
        )

    @depends_on("Determination", check=FALSEY)
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

    def _validate_category_consistency(self, cleaned_data):
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

    @depends_on("Age Range", check=NOT_EQUAL(u"U"))
    def _validate_dob_present(self, cleaned_data):
        validate_present(cleaned_data.get("DOB"), "A date of birth is required unless" " Age range is set to 'U'")

    @depends_on("Determination", check=TRUTHY)
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

    @depends_on("Exempted Code Reason", check=TRUTHY)
    @depends_on("Determination", check=FALSEY)
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

    @depends_on("Determination", check=FALSEY)
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

    @depends_on("Determination", check=TRUTHY)
    def _validate_determination_dvca_is_family(self, cleaned_data, category):
        determination = cleaned_data.get("Determination")
        if determination == u"DVCA" and category != u"family":
            raise serializers.ValidationError("Category (%s) must be Family if Determination is DVCA" % category)

    @staticmethod
    def format_message(s, row_num):
        return "Row: %s - %s" % (row_num + 1, s)

    def _validate_data(self, cleaned_data, row_num):
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
