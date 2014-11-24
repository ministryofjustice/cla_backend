from decimal import Decimal, InvalidOperation
import datetime
import re

from rest_framework import serializers
from dateutil.parser import parse


SERVICE_ADAPTATIONS = {u'CBI', u'LLI', u'BSL', u'MIN', u'TYP', u'SWC', u'AOD',
                      u'TPC', u'TAF', u'FRS', u'NAR', u'OTH', u'MAR'}

EXEMPTION_CODES = {u'ECHI', u'EDET', u'EPRE'}

DISABILITY_INDICATOR = {u'NCD', u'MHC', u'LDD', u'ILL', u'OTH', u'UKN', u'MOB', u'DEA',
                        u'HEA',u'VIS',u'BLI',u'PNS',u'PHY',u'SEN',u'COG'}

def validate_decimal(val):
    if val:
        try:
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


def validate_present(val):
    if not val.strip():
        raise serializers.ValidationError('is required')
    return val


def validate_date(val):
    val = val.strip()
    if val:
        try:
            val = parse(val, dayfirst=True)
            return val
        except (ValueError, TypeError) as ve:
            raise serializers.ValidationError('%s is not a valid date' % val)


def validate_not_present(val):
    if val.strip():
        raise serializers.ValidationError('Field should not be present')
    return val


def validate_regex(regex, flags=None):
    compiled_re = re.compile(regex, flags)

    def _validate_regex(val):
        if val and (not compiled_re.match(val)):
            raise serializers.ValidationError(
                'Field doesn\'t match pattern: %s' % regex)
        return val

    return _validate_regex

def validate_in(iterable):
    def _validate_in(val):
        if val and (not val in iterable):
            raise serializers.ValidationError('%s must be one of %s' % (val, ', '.join(iterable)))
        return val
    return _validate_in

def inverted_reduce(x, f):
    return f(x)

class ProviderCSVValidator(object):
    # the index is the offset in the csv
    fields = (
        # 'name', iterable of validators to apply
        ('CLA Reference Number', [validate_present, validate_integer]),  #1
        ('Client Ref', [validate_present]),  #2
        ('Account Number', [validate_present,
                            validate_regex(r'\d{1}[a-z]{1}\d{3}[a-z]{1}',
                                           re.IGNORECASE)]),  #3
        ('First Name', [validate_present]),  #4
        ('Surname', [validate_present]),  #5
        ('DOB', [validate_present, validate_date]),  #6
        ('Age Range', [validate_present]),  #7
        ('Gender', [validate_present]),  #8
        ('Ethnicity', [validate_present]),  #9
        ('Unused1', [validate_not_present]),  #10
        ('Unused2', [validate_not_present]),  #11
        ('Postcode', [validate_present]),  #12
        ('Eligibility', []),  #13
        ('Matter Type 1', [validate_present]),  #14
        ('Matter Type 2', [validate_present]),  #15
        ('Stage Reached', []),  #16
        ('Outcome Code', []),  #17
        ('Unused3', [validate_not_present]),  #18
        ('Date Opened', [validate_date]),  #19
        ('Date Closed', [validate_date]),  #20
        ('Time Spent', [validate_integer]),  #21
        ('Case Costs', [validate_present, validate_decimal]),  #22
        ('Unused4', [validate_not_present]),  #23
        ('Disability Code', [validate_present, validate_in(DISABILITY_INDICATOR)]),  #24
        ('Disbursements', [validate_decimal]),  #25
        ('Travel Costs', [validate_decimal]),  #26
        ('Determination', []),  #27
        ('Suitable for Telephone Advice', []),  #28
        ('Exceptional Cases (ref)', [validate_regex(r'\d{7}[a-z]{2}', re.I)]),  #29
        ('Exempted Reason Code', [validate_in(EXEMPTION_CODES)]),  #30
        ('Adjustments / Adaptations', [validate_in(SERVICE_ADAPTATIONS)]),  #31
        ('Signposting / Referral', []),  #32
        ('Media Code', []),
        #33 TODO: Maybe put [validate_present]) back depending on reply from Alex A.
        ('Telephone / Online', [validate_present]),  #34
    )

    def __init__(self, rows):
        self.rows = rows
        self.cleaned_data = []

    def _validate_field(self, field_name, field_value, idx,
                        row_num, validators):
        # Field Validation
        try:
            # reduce the validators over the original field value, save
            # the final value into self.cleaned_data[field_name]
            cleaned_value = reduce(inverted_reduce, validators,
                                   field_value)

            return cleaned_value

        except serializers.ValidationError as ve:
            ve.message = 'Row: %s Field (%s): %s - %s' % (
                row_num + 1, idx + 1, field_name, ve.message)
            raise ve

    def _validate_fields(self):
        """
        Validate individual field values, like django's clean_<fieldname> with
        less magic ( no setattr('clean_'+field_name) junk) just loop over
        the fields and apply the validators specified in the
        field spec (self.fields)
        """
        cleaned_data = {}



        for row_num, row in enumerate(self.rows):
            if len(row) != len(self.fields):
                raise serializers.ValidationError(
                    'Row: %s - Incorrect number of columns should be %s '
                    'actually %s' % (row_num + 1, len(self.fields), len(row)))


            for idx, field_value in enumerate(row):
                field_name, validators = self.fields[idx]
                cleaned_data[field_name] = self._validate_field(field_name, field_value,
                                     idx, row_num, validators)

            # Global Validation
            self.cleaned_data.append(self._validate_data(cleaned_data, row_num))

    def _validate_open_closed_date(self, cleaned_data):
        if not cleaned_data.get('Determination'):
            opened = cleaned_data.get('Date Opened')
            closed = cleaned_data.get('Date Closed')
            if (opened and closed) and (closed < opened):
                raise serializers.ValidationError(
                    'Closed date (%s) must be after opened date (%s)' % (
                    closed, opened))

    def _validate_service_adaptation(self, cleaned_data):
        if not cleaned_data.get('Determination'):
            opened = cleaned_data.get('Date Opened')
            if opened > datetime.datetime(2013, 4, 1):
                validate_present(cleaned_data.get('Adjustments / Adaptations'))

    def _validate_media_code(self, cleaned_data):
        if not cleaned_data.get('Determination'):
            validate_present(cleaned_data.get('Media Code'))

    def _validate_data(self, cleaned_data, row_num):
        """
        Like django's clean method, use this to validate across fields
        """
        try:
            self._validate_open_closed_date(cleaned_data)
            self._validate_service_adaptation(cleaned_data)
            self._validate_media_code(cleaned_data)

            return cleaned_data
        except serializers.ValidationError as ve:
            ve.message = 'Row: %s - %s' % (
                row_num + 1, ve.message)
            raise ve


    def validate(self):
        self._validate_fields()
        return self.cleaned_data
