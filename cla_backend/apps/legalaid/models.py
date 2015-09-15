import logging
import datetime
from django.utils import timezone

from jsonfield import JSONField

from uuidfield import UUIDField
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import SET_NULL
from django.conf import settings
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist

from model_utils.models import TimeStampedModel

from core.utils import getattrd
from core.cloning import clone_model, CloneModelMixin

from eligibility_calculator.models import CaseData
from eligibility_calculator.calculator import EligibilityChecker
from eligibility_calculator.exceptions import PropertyExpectedException

from diagnosis.models import DiagnosisTraversal

from cla_common.db.mixins import ModelDiffMixin
from cla_common.money_interval.fields import MoneyIntervalField
from cla_common.money_interval.models import MoneyInterval
from cla_common.constants import ELIGIBILITY_STATES, THIRDPARTY_REASON, \
    THIRDPARTY_RELATIONSHIP, ADAPTATION_LANGUAGES, MATTER_TYPE_LEVELS, \
    CONTACT_SAFETY, EXEMPT_USER_REASON, ECF_STATEMENT, REQUIRES_ACTION_BY, \
    EMAIL_SAFETY, ELIGIBILITY_REASONS, EXPRESSIONS_OF_DISSATISFACTION

from legalaid.fields import MoneyField

from cla_common.constants import CASE_SOURCE


logger = logging.getLogger(__name__)


def _make_reference():
    from django.utils.crypto import get_random_string

    return u'%s-%s-%s' % (
        # exclude B8G6I1l0OQDS5Z2
        get_random_string(length=2,
                          allowed_chars='ACEFHJKMNPRTUVWXY3479'),
        get_random_string(length=4, allowed_chars='123456789'),
        get_random_string(length=4, allowed_chars='123456789')
    )


def _check_reference_unique(reference):
    return not Case.objects.filter(reference=reference).exists()


class Category(TimeStampedModel):
    name = models.CharField(max_length=500)
    code = models.CharField(max_length=50, unique=True)
    raw_description = models.TextField(blank=True)
    ecf_available = models.BooleanField(default=False)
    mandatory = models.BooleanField(default=False)
    description = models.TextField(blank=True, editable=False)
    order = models.PositiveIntegerField(default=0)

    class Meta(object):
        ordering = ['order']
        verbose_name_plural = "categories"

    def __unicode__(self):
        return u'%s' % self.name


class Savings(CloneModelMixin, TimeStampedModel):
    bank_balance = MoneyField(default=None, null=True, blank=True)
    investment_balance = MoneyField(default=None, null=True, blank=True)
    asset_balance = MoneyField(default=None, null=True, blank=True)
    credit_balance = MoneyField(default=None, null=True, blank=True)

    cloning_config = {
        'excludes': ['created', 'modified']
    }


class Income(CloneModelMixin, TimeStampedModel):
    earnings = MoneyIntervalField(default=None, null=True, blank=True)
    self_employment_drawings = MoneyIntervalField(default=None, null=True, blank=True)
    benefits = MoneyIntervalField(default=None, null=True, blank=True)
    tax_credits = MoneyIntervalField(default=None, null=True, blank=True)
    child_benefits = MoneyIntervalField(default=None, null=True, blank=True)
    maintenance_received = MoneyIntervalField(default=None, null=True, blank=True)
    pension = MoneyIntervalField(default=None, null=True, blank=True)
    other_income = MoneyIntervalField(default=None, null=True, blank=True)
    self_employed = models.NullBooleanField(default=None)

    cloning_config = {
        'excludes': ['created', 'modified']
    }


class Deductions(CloneModelMixin, TimeStampedModel):
    income_tax = MoneyIntervalField(default=None, null=True, blank=True)
    national_insurance = MoneyIntervalField(default=None, null=True,
                                            blank=True)
    maintenance = MoneyIntervalField(default=None, null=True, blank=True)
    childcare = MoneyIntervalField(default=None, null=True, blank=True)
    mortgage = MoneyIntervalField(default=None, null=True, blank=True)
    rent = MoneyIntervalField(default=None, null=True, blank=True)
    criminal_legalaid_contributions = MoneyField(default=None, null=True,
                                                 blank=True)

    cloning_config = {
        'excludes': ['created', 'modified']
    }


class PersonalDetails(CloneModelMixin, TimeStampedModel):
    title = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=400, blank=True, null=True)
    postcode = models.CharField(max_length=12, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    home_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    ni_number = models.CharField(max_length=10, null=True, blank=True)
    contact_for_research = models.NullBooleanField(blank=True, null=True)
    vulnerable_user = models.NullBooleanField(blank=True, null=True)
    safe_to_contact = models.CharField(
        max_length=30,
        default=CONTACT_SAFETY.SAFE,
        choices=CONTACT_SAFETY,
        blank=True, null=True)
    safe_to_email = models.CharField(
        max_length=20,
        default=EMAIL_SAFETY.SAFE,
        choices=EMAIL_SAFETY,
        blank=True, null=True)
    case_count = models.PositiveSmallIntegerField(default=0)

    reference = UUIDField(auto=True, unique=True)
    diversity = models.BinaryField(blank=True, null=True, editable=False)
    diversity_modified = models.DateTimeField(
        auto_now=False, blank=True, null=True, editable=False
    )

    # only normalised version of post code for now
    search_field = models.TextField(null=True, blank=True, db_index=True)

    cloning_config = {
        'excludes': ['reference', 'created', 'modified', 'case_count', 'search_field']
    }

    class Meta(object):
        verbose_name_plural = "personal details"

    def __unicode__(self):
        return u'%s' % self.full_name

    def _set_search_field(self):
        if self.postcode:
            self.search_field =  self.postcode.replace(' ', '')

    def save(self, *args, **kwargs):
        self._set_search_field()
        super(PersonalDetails, self).save(*args, **kwargs)

    def update_case_count(self):
        case_count = self.case_set.count()

        # avoiding an extra save if possible
        if case_count != self.case_count:
            self.case_count = case_count
            self.save(update_fields=['case_count'])


class ThirdPartyDetails(CloneModelMixin, TimeStampedModel):
    personal_details = models.ForeignKey(PersonalDetails)
    pass_phrase = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=30, choices=THIRDPARTY_REASON, null=True, blank=True, default='')
    personal_relationship = models.CharField(max_length=30,
                                             choices=THIRDPARTY_RELATIONSHIP)
    personal_relationship_note = models.CharField(max_length=255, blank=True)
    spoke_to = models.NullBooleanField(blank=True, null=True)
    no_contact_reason = models.TextField(blank=True, null=True)
    organisation_name = models.CharField(max_length=255, blank=True, null=True)

    reference = UUIDField(auto=True, unique=True)

    cloning_config = {
        'excludes': ['reference', 'created', 'modified'],
        'clone_fks': ['personal_details']
    }

    class Meta(object):
        verbose_name_plural = "third party details"

    def __unicode__(self):
        return u'%s' % self.personal_details.full_name


class AdaptationDetails(CloneModelMixin, TimeStampedModel):
    bsl_webcam = models.BooleanField(default=False)
    minicom = models.BooleanField(default=False)
    text_relay = models.BooleanField(default=False)
    skype_webcam = models.BooleanField(default=False)
    language = models.CharField(max_length=30, choices=ADAPTATION_LANGUAGES,
                                blank=True, null=True)
    notes = models.TextField(blank=True)
    callback_preference = models.BooleanField(default=False)
    reference = UUIDField(auto=True, unique=True)

    cloning_config = {
        'excludes': ['reference', 'created', 'modified']
    }


class EODDetailsManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(EODDetailsManager, self).get_queryset().select_related(
            'case'
        )


class EODDetails(TimeStampedModel):
    case = models.OneToOneField('Case', related_name='eod_details')
    notes = models.TextField(blank=True)
    reference = UUIDField(auto=True, unique=True)

    objects = EODDetailsManager()

    class Meta(object):
        ordering = ('-created',)
        verbose_name = 'EOD details'
        verbose_name_plural = 'EOD details'

    def __unicode__(self):
        return u'EOD on case %s' % self.case

    @classmethod
    def get_eod_stats(cls):
        data = dict(EODDetailsCategory.objects.values_list('category').
                    annotate(count=models.Count('category')))
        return {
            'total_count': sum(data.values()),
            'categories': [
                {
                    'description': description,
                    'count': data.get(category, 0),
                }
                for category, description in EXPRESSIONS_OF_DISSATISFACTION.CHOICES
            ]
        }

    @property
    def is_major(self):
        return self.categories.filter(is_major=True).exists()

    def get_category_descriptions(self, include_severity=False):
        mapper = (lambda cat: unicode(cat) + (u' (Major)' if cat.is_major else u' (Minor)')) if include_severity else unicode
        return list(map(mapper, self.categories.all()))


class EODDetailsCategory(models.Model):
    eod_details = models.ForeignKey(EODDetails, related_name='categories')
    category = models.CharField(max_length=30, choices=EXPRESSIONS_OF_DISSATISFACTION,
                                blank=True, null=True)
    is_major = models.BooleanField(default=False)

    class Meta(object):
        verbose_name = 'EOD category'
        verbose_name_plural = 'EOD categories'

    def __unicode__(self):
        return EXPRESSIONS_OF_DISSATISFACTION.CHOICES_DICT.get(self.category)


class Person(CloneModelMixin, TimeStampedModel):
    income = models.ForeignKey(Income, blank=True, null=True)
    savings = models.ForeignKey(Savings, blank=True, null=True)
    deductions = models.ForeignKey(Deductions, blank=True, null=True)

    cloning_config = {
        'excludes': ['created', 'modified'],
        'clone_fks': ['income', 'savings', 'deductions']
    }

    class Meta(object):
        ordering = ('-created',)
        verbose_name_plural = 'people'

    @classmethod
    def from_dict(cls, d):
        income = None
        savings = None
        deductions = None
        if d:
            income_dict = d.get('income')
            savings_dict = d.get('savings')
            deductions_dict = d.get('deductions')
            if income_dict:
                income = Income(**income_dict)
            if savings_dict:
                savings = Savings(**savings_dict)
            if deductions_dict:
                deductions = Deductions(**deductions_dict)

        return Person(
            income=income,
            savings=savings,
            deductions=deductions)


class ValidateModelMixin(models.Model):
    class Meta(object):
        abstract = True

    def get_dependencies(self):
        """
        implement this in the model class that you
        use the mixin inside of.
        :return: a set of fields that are required given
        the current state of the saved object. You can reference
        nested fields by using __ notation. e.g. `partner__income`
        """
        raise NotImplementedError()

    def validate(self):
        dependencies = self.get_dependencies()
        warnings = {}
        for dep in dependencies:
            if not getattrd(self, dep, None):
                if '__' in dep:
                    levels = dep.split('__')
                    current = warnings
                    for level in levels:
                        if not level == levels[-1]:
                            current = warnings.get(level, {})
                            warnings[level] = current
                        else:
                            current[level] = ['Field "%s" is required' % level]
                else:
                    warnings[dep] = ['Field "%s" is required' % dep]
        return {"warnings": warnings}


class EligibilityCheck(TimeStampedModel, ValidateModelMixin, ModelDiffMixin):
    reference = UUIDField(auto=True, unique=True)

    category = models.ForeignKey(Category, blank=True, null=True)
    you = models.ForeignKey(Person, blank=True, null=True, related_name='you')
    partner = models.ForeignKey(Person, blank=True, null=True,
                                related_name='partner')
    disputed_savings = models.ForeignKey(Savings, blank=True, null=True)
    your_problem_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    state = models.CharField(
        max_length=50, default=ELIGIBILITY_STATES.UNKNOWN,
        choices=ELIGIBILITY_STATES.CHOICES
    )
    dependants_young = models.PositiveIntegerField(null=True, blank=True,
                                                   default=None, validators=[
            MaxValueValidator(50)]
    )
    dependants_old = models.PositiveIntegerField(null=True, blank=True,
                                                 default=None, validators=[
            MaxValueValidator(50)]
    )
    on_passported_benefits = models.NullBooleanField(default=None)
    on_nass_benefits = models.NullBooleanField(default=None)
    specific_benefits = JSONField(null=True, blank=True)

    # need to be moved into graph/questions format soon
    is_you_or_your_partner_over_60 = models.NullBooleanField(default=None)
    has_partner = models.NullBooleanField(default=None)

    calculations = JSONField(null=True, blank=True)

    class Meta(object):
        ordering = ('-created',)

    def __unicode__(self):
        return u'EligibilityCheck(%s)' % self.reference

    def get_dependencies(self):
        deps = {'category',
                'you__income',
                'you__savings',
                'you__deductions'}

        if self.has_partner:
            deps.update({
                'partner__income',
                'partner__savings',
                'partner__deductions'
            })

        return deps

    def get_eligibility_state(self):
        """
        Returns one of the ELIGIBILITY_STATES values depending on if the model
        is eligible or not. If PropertyExpectedException is raised, it means
        that we don't have enough data to determine the state so we set the
        `state` property to UNKNOWN.
        """
        ec = EligibilityChecker(self.to_case_data())

        try:
            if ec.is_eligible():
                return ELIGIBILITY_STATES.YES, ec, []
            else:
                return ELIGIBILITY_STATES.NO, ec, self.get_ineligible_reason(ec)
        except PropertyExpectedException:
            return ELIGIBILITY_STATES.UNKNOWN, ec, []

    def get_ineligible_reason(self, ec=None):
        ec = ec or EligibilityChecker(self.to_case_data())
        reasons = []

        def add_reason(meth, reason):
            try:
                if not meth():
                    reasons.append(reason)
            except PropertyExpectedException:
                pass

        add_reason(ec.is_disposable_capital_eligible,
                   ELIGIBILITY_REASONS.DISPOSABLE_CAPITAL)
        add_reason(ec.is_gross_income_eligible,
                   ELIGIBILITY_REASONS.GROSS_INCOME)
        add_reason(ec.is_disposable_income_eligible,
                   ELIGIBILITY_REASONS.DISPOSABLE_INCOME)

        return reasons

    def update_state(self):
        self.state, checker, reasons = self.get_eligibility_state()

        if self.state == ELIGIBILITY_STATES.UNKNOWN:
            self.calculations = None
        else:
            self.calculations = checker.calcs

        self.save()

    def has_stated_any_specific_benefits(self):
        if not self.specific_benefits:
            return False
        return any(self.specific_benefits.values())

    def to_case_data(self):
        def compose_dict(model=self, props=None):
            if not props:
                props = []
            if not model:
                return None

            obj = {}
            for prop in props:
                value = getattr(model, prop)
                if value is not None:
                    if isinstance(value, MoneyInterval):
                        value = value.as_monthly()
                    obj[prop] = value
            return obj

        d = {}

        if self.category:
            d['category'] = self.category.code

        d['property_data'] = self.property_set.values(
            'value', 'mortgage_left', 'share', 'disputed', 'main'
        )

        d['facts'] = compose_dict(props=[
            'dependants_old', 'dependants_young', 'has_partner',
            'is_you_or_your_partner_over_60',
        ])

        d['facts']['on_passported_benefits'] = self.on_passported_benefits
        d['facts']['on_nass_benefits'] = self.on_nass_benefits

        if self.you:
            you_props = {
                'savings': compose_dict(self.you.savings, [
                    'bank_balance', 'investment_balance', 'credit_balance',
                    'asset_balance'
                ]),
                'income': compose_dict(self.you.income, [
                    'earnings', 'self_employment_drawings', 'benefits',
                    'tax_credits', 'child_benefits', 'maintenance_received',
                    'pension', 'other_income', 'self_employed'
                ]),
                'deductions': compose_dict(self.you.deductions, [
                    'income_tax', 'national_insurance', 'maintenance',
                    'childcare', 'mortgage', 'rent',
                    'criminal_legalaid_contributions'
                ])
            }
            d['you'] = {prop: value for prop, value in you_props.items() if
                        value}

        if self.has_partner and self.partner:
            partner_income = compose_dict(self.partner.income, [
                'earnings', 'self_employment_drawings', 'benefits',
                'tax_credits', 'maintenance_received', 'child_benefits',
                'pension', 'other_income', 'self_employed'
            ])

            # If partner.income.child_benefits is None, this method will use a
            # default value (0). This is because that field is not exposed yet
            # (partner's child benefits can't be provided with).
            # Used this because in the future I reckon this might change so
            # it would be easier to support.
            if partner_income and 'child_benefits' not in partner_income:
                partner_income['child_benefits'] = 0

            partner_props = {
                'savings': compose_dict(self.partner.savings, [
                    'bank_balance', 'investment_balance', 'credit_balance',
                    'asset_balance'
                ]),
                'income': partner_income,
                'deductions': compose_dict(self.partner.deductions, [
                    'income_tax', 'national_insurance', 'maintenance',
                    'childcare', 'mortgage', 'rent',
                    'criminal_legalaid_contributions'
                ])
            }
            d['partner'] = {prop: value for prop, value in
                            partner_props.items() if value}

        if self.disputed_savings:
            d['disputed_savings'] = compose_dict(
                self.disputed_savings, [
                    'bank_balance', 'investment_balance', 'credit_balance',
                    'asset_balance'
                ])

        # Fake
        d['facts']['is_partner_opponent'] = False

        return CaseData(**d)

    def reset_matter_types(self):
        case = None

        try:
            case = self.case
        except ObjectDoesNotExist:
            pass

        if case and (case.matter_type1 or self.case.matter_type2):
            case.matter_type1 = None
            case.matter_type2 = None
            case.save()


class Property(TimeStampedModel):
    value = MoneyField(default=None, null=True, blank=True)
    mortgage_left = MoneyField(default=None, null=True, blank=True)
    share = models.PositiveIntegerField(default=None,
                                        validators=[MaxValueValidator(100)],
                                        null=True, blank=True)
    eligibility_check = models.ForeignKey(EligibilityCheck, related_query_name='property_set')
    disputed = models.NullBooleanField(default=None)
    main = models.NullBooleanField(default=None)

    class Meta(object):
        verbose_name_plural = 'properties'
        ordering = ('-created',)


class MatterType(TimeStampedModel):
    category = models.ForeignKey(Category)
    code = models.CharField(max_length=4)
    description = models.CharField(max_length=255)
    level = models.PositiveSmallIntegerField(
        choices=MATTER_TYPE_LEVELS.CHOICES,
        validators=[MaxValueValidator(2)])

    def __unicode__(self):
        return u'MatterType{} ({}): {} - {}'.format(
            self.get_level_display(), self.category.code, self.code, self.description)

    class Meta(object):
        unique_together = (("code", "level"),)


class MediaCodeGroup(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class MediaCode(TimeStampedModel):
    group = models.ForeignKey(MediaCodeGroup)
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=20)


class Case(TimeStampedModel, ModelDiffMixin):
    reference = models.CharField(max_length=128, unique=True, editable=False)
    eligibility_check = models.OneToOneField(EligibilityCheck, null=True,
                                             blank=True)
    diagnosis = models.OneToOneField('diagnosis.DiagnosisTraversal', null=True,
                                     blank=True, on_delete=SET_NULL)
    personal_details = models.ForeignKey(PersonalDetails, blank=True,
                                         null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                   null=True)

    requires_action_by = models.CharField(
        max_length=50, choices=REQUIRES_ACTION_BY.CHOICES,
        default=REQUIRES_ACTION_BY.OPERATOR,
        blank=True, null=True, editable=False
    )

    requires_action_at = models.DateTimeField(
        auto_now=False, blank=True, null=True
    )
    callback_attempt = models.PositiveSmallIntegerField(default=0)

    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        related_name='case_locked'
    )
    locked_at = models.DateTimeField(auto_now=False, blank=True, null=True)
    provider = models.ForeignKey('cla_provider.Provider', blank=True,
                                 null=True)
    notes = models.TextField(blank=True)
    provider_notes = models.TextField(blank=True)
    laa_reference = models.BigIntegerField(
        null=True, blank=True, unique=True, editable=False
    )
    thirdparty_details = models.ForeignKey('ThirdPartyDetails', blank=True,
                                           null=True)
    adaptation_details = models.ForeignKey('AdaptationDetails', blank=True,
                                           null=True)
    billable_time = models.PositiveIntegerField(default=0)

    matter_type1 = models.ForeignKey(MatterType,
                                     limit_choices_to=
                                     {'level': MATTER_TYPE_LEVELS.ONE},
                                     blank=True, null=True,
                                     related_name='+')

    matter_type2 = models.ForeignKey(MatterType,
                                     limit_choices_to=
                                     {'level': MATTER_TYPE_LEVELS.TWO},
                                     blank=True, null=True,
                                     related_name='+')

    media_code = models.ForeignKey(MediaCode, blank=True, null=True)

    alternative_help_articles = models.ManyToManyField('knowledgebase.Article',
                                                       through='CaseKnowledgebaseAssignment',
                                                       null=True, blank=True)

    outcome_code = models.CharField(max_length=50, blank=True, null=True)
    outcome_code_id = models.IntegerField(null=True, blank=True)
    level = models.PositiveSmallIntegerField(null=True)

    # exempt user is a property of case
    exempt_user = models.NullBooleanField(blank=True, null=True)
    exempt_user_reason = models.CharField(blank=True, null=True, max_length=5, choices=EXEMPT_USER_REASON)

    # exceptional case fund
    ecf_statement = models.CharField(blank=True, null=True, max_length=35, choices=ECF_STATEMENT)

    # if not None, indicates the case from which this was created
    #   that is, the original case being split
    from_case = models.ForeignKey('self', blank=True, null=True, related_name='split_cases')

    provider_assigned_at = models.DateTimeField(blank=True, null=True)
    provider_viewed = models.DateTimeField(blank=True, null=True)
    provider_accepted = models.DateTimeField(blank=True, null=True)
    provider_closed = models.DateTimeField(blank=True, null=True)
    source = models.CharField(
        max_length=20, choices=CASE_SOURCE, default=CASE_SOURCE.PHONE
    )

    # for now it's a '-' stripped version of the reference only
    # we could start getting smart and putting in all permutations of
    # a reference x ambiguous characters but not for now
    search_field = models.TextField(null=True, blank=True, db_index=True)

    complaint_flag = models.BooleanField(default=False)

    class Meta(object):
        ordering = ('-created',)
        permissions = (
            ('run_reports', u'Can run reports'),
            ('run_obiee_reports', u'Can run OBIEE reports'),
            ('run_complaints_report', u'Can run complaints report'),
        )

    def __unicode__(self):
        return self.reference

    def _set_reference_if_necessary(self):
        max_retries = 10
        tries = 0
        if not self.reference:
            reference = _make_reference()
            while (not _check_reference_unique(reference) and tries < max_retries):
                reference = _make_reference()
                tries += 1

            self.reference = reference

    def _set_search_field(self):
        if self.reference:
            self.search_field = self.reference.replace('-', '')

    def is_part_of_split(self):
        """
        Returns True if self has been generated or it generated cases via a split case action.
        """
        return self.from_case or self.split_cases.count() > 0

    def split(self, user, category, matter_type1, matter_type2, assignment_internal):
        # DIAGNOSIS
        diagnosis = DiagnosisTraversal.objects.create_eligible(category)

        # ELIGIBILITY CHECK
        eligibility_check = clone_model(
            cls=EligibilityCheck,
            pk=self.eligibility_check_id,
            config={
                'excludes': ['reference', 'created', 'modified'],
                'clone_fks': ['you', 'partner', 'disputed_savings'],
                'override_values': {
                    'category': category
                }
            }
        )
        if self.eligibility_check:
            prop_ids = self.eligibility_check.property_set.values_list('pk', flat=True)
            for prop_id in prop_ids:
                clone_model(cls=Property, pk=prop_id, config={
                    'excludes': ['created', 'modified'],
                    'override_values': {
                        'eligibility_check': eligibility_check
                    }
                })

        # CASE
        override_values = {
            'eligibility_check': eligibility_check,
            'diagnosis': diagnosis,
            'created_by': user,
            'matter_type1': matter_type1,
            'matter_type2': matter_type2,
            'from_case': self,
            'provider_viewed': None,
            'provider_accepted': None,
            'provider_closed': None,
        }
        if assignment_internal:
            override_values['requires_action_by'] = self.requires_action_by
            override_values['provider_assigned_at'] = self.provider_assigned_at
        else:
            override_values['provider'] = None
            override_values['requires_action_by'] = REQUIRES_ACTION_BY.OPERATOR
            override_values['provider_assigned_at'] = None

        new_case = clone_model(
            cls=self.__class__,
            pk=self.pk,
            config={
                'excludes': [
                    'reference', 'locked_by', 'locked_at',
                    'laa_reference', 'billable_time', 'outcome_code', 'level',
                    'created', 'modified', 'outcome_code_id', 'requires_action_at',
                    'callback_attempt', 'search_field', 'provider_assigned_at',
                ],
                'clone_fks': [
                    'thirdparty_details', 'adaptation_details',
                ],
                'override_values': override_values
            }
        )
        for cka_id in self.caseknowledgebaseassignment_set.values_list('pk', flat=True):
            clone_model(cls=CaseKnowledgebaseAssignment, pk=cka_id, config={
                'override_values': {
                    'case': new_case
                }
            })
        return new_case

    def save(self, *args, **kwargs):
        self._set_reference_if_necessary()
        self._set_search_field()

        if not self.pk:
            super(Case, self).save(*args, **kwargs)
            self.laa_reference = self.pk + settings.LAA_REFERENCE_SEED
            kwargs['force_insert'] = False
            self.save(*args, **kwargs)
        else:
            super(Case, self).save(*args, **kwargs)

        # updating personal_details case count
        if self.personal_details:
            self.personal_details.update_case_count()

    def assign_to_provider(self, provider):
        self.provider = provider
        self.provider_assigned_at = timezone.now()
        self.provider_viewed = None
        self.provider_accepted = None
        self.provider_closed = None
        self.save(update_fields=[
            'provider', 'provider_viewed', 'provider_accepted',
            'provider_closed', 'modified', 'provider_assigned_at'
        ])
        self.reset_requires_action_at()

    def view_by_provider(self, provider):
        if provider == self.provider:
            self.provider_viewed = datetime.datetime.utcnow().replace(tzinfo=utc)
            self.save(update_fields=['provider_viewed'])

    def accept_by_provider(self):
        self.provider_accepted = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save(update_fields=['provider_accepted'])

    def close_by_provider(self):
        self.provider_closed = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save(update_fields=['provider_closed'])

    def reopen_by_provider(self):
        self.provider_closed = None
        self.save(update_fields=['provider_closed'])

    def assign_alternative_help(self, user, articles):
        self.alternative_help_articles.clear()
        for article in articles:
            CaseKnowledgebaseAssignment.objects.create(case=self,
                                                       alternative_help_article=article,
                                                       assigned_by=user)
        self.reset_requires_action_at()

    def lock(self, user, save=True):
        if not self.locked_by:
            self.locked_by = user
            self.locked_at = datetime.datetime.utcnow().replace(tzinfo=utc)
            if save:
                self.save(update_fields=['locked_by', 'locked_at'])
            return True
        else:
            if self.locked_by != user:
                logger.warning(
                    u'User %s tried to lock case %s locked already by %s' % (
                        user, self.reference, self.locked_by
                    ))

        return False

    def set_requires_action_by(self, requires_action_by):
        self.requires_action_by = requires_action_by
        self.save(update_fields=['requires_action_by', 'modified'])

    def set_requires_action_at(self, requires_action_at):
        self.requires_action_at = requires_action_at
        self.callback_attempt += 1
        self.save(update_fields=['requires_action_at', 'callback_attempt', 'modified'])

    def reset_requires_action_at(self):
        if self.requires_action_at != None or self.callback_attempt != 0:
            self.requires_action_at = None
            self.callback_attempt = 0
            self.save(update_fields=['requires_action_at', 'callback_attempt', 'modified'])

    @property
    def doesnt_requires_action(self):
        return not self.requires_action_by

    @property
    def requires_action_by_operator(self):
        return self.requires_action_by == REQUIRES_ACTION_BY.OPERATOR

    @property
    def requires_action_by_operator_manager(self):
        return self.requires_action_by == REQUIRES_ACTION_BY.OPERATOR_MANAGER


class CaseNotesHistory(TimeStampedModel):
    case = models.ForeignKey(Case, db_index=True)
    operator_notes = models.TextField(null=True, blank=True)
    provider_notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    include_in_summary = models.BooleanField(default=True)

    class Meta(object):
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        self.include_in_summary = True
        super(CaseNotesHistory, self).save(*args, **kwargs)

        qs = CaseNotesHistory.objects.filter(
            case=self.case,
            created__gte=timezone.now() - datetime.timedelta(minutes=30),
            created_by=self.created_by
        ).exclude(pk=self.pk)
        qs.update(include_in_summary=False)


class CaseKnowledgebaseAssignment(TimeStampedModel):
    case = models.ForeignKey(Case)
    alternative_help_article = models.ForeignKey('knowledgebase.Article')
    assigned_by = models.ForeignKey('auth.User', blank=True, null=True)
