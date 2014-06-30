import logging
import datetime
import uuid
from uuidfield import UUIDField
from model_utils.models import TimeStampedModel

from django.core.validators import MaxValueValidator
from django.db import models
from django.conf import settings
from django.db.models import F
from django.utils.timezone import utc

from eligibility_calculator.models import CaseData
from eligibility_calculator.calculator import EligibilityChecker
from eligibility_calculator.exceptions import PropertyExpectedException

from call_centre.utils import getattrd

# from jsonfield import JSONField

from cla_common.money_interval.fields import MoneyIntervalField
from cla_common.money_interval.models import MoneyInterval
from cla_common.constants import ELIGIBILITY_STATES, CASE_STATES, THIRDPARTY_REASON,\
                                 THIRDPARTY_RELATIONSHIP, ADAPTATION_LANGUAGES


from legalaid.exceptions import InvalidMutationException
from legalaid.fields import MoneyField


logger = logging.getLogger(__name__)


class Category(TimeStampedModel):
    name = models.CharField(max_length=500)
    code = models.CharField(max_length=50, unique=True)
    raw_description = models.TextField(blank=True)
    description = models.TextField(blank=True, editable=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "categories"

    def __unicode__(self):
        return u'%s' % self.name


class Savings(TimeStampedModel):
    bank_balance = MoneyField(default=None, null=True, blank=True)
    investment_balance = MoneyField(default=None, null=True, blank=True)
    asset_balance = MoneyField(default=None, null=True, blank=True)
    credit_balance = MoneyField(default=None, null=True, blank=True)


class Income(TimeStampedModel):
    earnings = MoneyIntervalField(default=None, null=True, blank=True)
    other_income = MoneyIntervalField(default=None, null=True, blank=True)
    self_employed = models.NullBooleanField(default=None)


class Deductions(TimeStampedModel):
    income_tax = MoneyIntervalField(default=None, null=True, blank=True)
    national_insurance = MoneyIntervalField(default=None, null=True, blank=True)
    maintenance = MoneyIntervalField(default=None, null=True, blank=True)
    childcare = MoneyIntervalField(default=None, null=True, blank=True)
    mortgage = MoneyIntervalField(default=None, null=True, blank=True)
    rent = MoneyIntervalField(default=None, null=True, blank=True)
    criminal_legalaid_contributions = MoneyField(default=None, null=True, blank=True)


class PersonalDetails(TimeStampedModel):
    title = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=400, blank=True, null=True)
    postcode = models.CharField(max_length=12, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    home_phone = models.CharField(max_length=20, blank=True)
    # email = models.EmailField(blank=True)

    reference = UUIDField(auto=True, unique=True)

    class Meta:
        verbose_name_plural = "personal details"

class ThirdPartyDetails(TimeStampedModel):
    personal_details = models.ForeignKey(PersonalDetails)
    pass_phrase = models.CharField(max_length=255)
    reason = models.CharField(max_length=30, choices=THIRDPARTY_REASON)
    personal_relationship = models.CharField(max_length=30, choices=THIRDPARTY_RELATIONSHIP)
    personal_relationship_note = models.CharField(max_length=255, blank=True)
    reference = UUIDField(auto=True, unique=True)

class AdaptationDetails(TimeStampedModel):
    bsl_webcam = models.BooleanField(default=False)
    minicom = models.BooleanField(default=False)
    text_relay = models.BooleanField(default=False)
    skype_webcam = models.BooleanField(default=False)
    language = models.CharField(max_length=30, choices=ADAPTATION_LANGUAGES, blank=True, null=True)
    notes = models.TextField(blank=True)
    callback_preference = models.BooleanField(default=False)
    reference = UUIDField(auto=True, unique=True)

class Person(TimeStampedModel):
    income = models.ForeignKey(Income, blank=True, null=True)
    savings = models.ForeignKey(Savings, blank=True, null=True)
    deductions = models.ForeignKey(Deductions, blank=True, null=True)

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

    class Meta:
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
                            warnings[level]= current
                        else:
                            current[level] = ['Field "%s" is required' % level]
                else:
                    warnings[dep] = ['Field "%s" is required' % dep]
        return {"warnings": warnings}


class EligibilityCheck(TimeStampedModel, ValidateModelMixin):
    reference = UUIDField(auto=True, unique=True)

    category = models.ForeignKey(Category, blank=True, null=True)
    you = models.ForeignKey(Person, blank=True, null=True, related_name='you')
    partner = models.ForeignKey(Person, blank=True, null=True, related_name='partner')
    your_problem_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    state = models.CharField(
        max_length=50, default=ELIGIBILITY_STATES.UNKNOWN,
        choices=ELIGIBILITY_STATES.CHOICES
    )
    dependants_young = models.PositiveIntegerField(null=True, blank=True,
        default=None, validators=[MaxValueValidator(50)]
    )
    dependants_old = models.PositiveIntegerField(null=True, blank=True,
        default=None, validators=[MaxValueValidator(50)]
    )
    on_passported_benefits = models.NullBooleanField(default=None)
    on_nass_benefits = models.NullBooleanField(default=None)


    # need to be moved into graph/questions format soon
    is_you_or_your_partner_over_60 = models.NullBooleanField(default=None)
    has_partner = models.NullBooleanField(default=None)

    def get_dependencies(self):
        deps =  {'category',
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
                return ELIGIBILITY_STATES.YES
            else:
                return ELIGIBILITY_STATES.NO
        except PropertyExpectedException as e:
            return ELIGIBILITY_STATES.UNKNOWN

        # TODO what do we do when we get a different exception? (which shouldn't happen)

    def update_state(self):
        self.state = self.get_eligibility_state()
        self.save()

    def to_case_data(self):
        def compose_dict(model=self, props=[]):
            if not model:
                return None

            obj = {}
            for prop in props:
                value = getattr(model, prop)
                if value != None:
                    if isinstance(value, MoneyInterval):
                        value = value.as_monthly()
                    obj[prop] = value
            return obj

        d = {}

        if self.category:
            d['category'] = self.category.code

        d['property_data'] = self.property_set.values_list(
            'value', 'mortgage_left', 'share', 'disputed'
        )

        d['facts'] = compose_dict(props=[
            'dependants_old', 'dependants_young', 'has_partner',
            'is_you_or_your_partner_over_60', 'on_passported_benefits',
            'on_nass_benefits'
        ])

        if self.you:
            you_props = {
                'savings': compose_dict(self.you.savings, [
                    'bank_balance', 'investment_balance', 'credit_balance',
                    'asset_balance'
                ]),
                'income': compose_dict(self.you.income, [
                    'earnings', 'other_income', 'self_employed'
                ]),
                'deductions': compose_dict(self.you.deductions, [
                    'income_tax', 'national_insurance', 'maintenance',
                    'childcare', 'mortgage', 'rent', 'criminal_legalaid_contributions'
                ])
            }
            d['you'] = {prop:value for prop, value in you_props.items() if value}

        if self.has_partner and self.partner:
            partner_props = {
                'savings': compose_dict(self.partner.savings, [
                    'bank_balance', 'investment_balance', 'credit_balance',
                    'asset_balance'
                ]),
                'income': compose_dict(self.partner.income, [
                    'earnings', 'other_income', 'self_employed'
                ]),
                'deductions': compose_dict(self.partner.deductions, [
                    'income_tax', 'national_insurance', 'maintenance',
                    'childcare', 'mortgage', 'rent', 'criminal_legalaid_contributions'
                ])
            }
            d['partner'] = {prop:value for prop, value in partner_props.items() if value}

        # Fake
        d['facts']['is_partner_opponent'] = False

        return CaseData(**d)



class Property(TimeStampedModel):
    value = MoneyField(default=None, null=True, blank=True)
    mortgage_left = MoneyField(default=None, null=True, blank=True)
    share = models.PositiveIntegerField(default=None, validators=[MaxValueValidator(100)], null=True, blank=True)
    eligibility_check = models.ForeignKey(EligibilityCheck)
    disputed = models.NullBooleanField(default=None)

    class Meta:
        verbose_name_plural = "properties"


class Case(TimeStampedModel):
    reference = models.CharField(max_length=128, unique=True, editable=False)
    eligibility_check = models.OneToOneField(EligibilityCheck, null=True, blank=True)
    personal_details = models.ForeignKey(PersonalDetails, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    state = models.CharField(
        max_length=50, choices=CASE_STATES.CHOICES, default=CASE_STATES.OPEN
    )
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        related_name='case_locked'
    )
    locked_at = models.DateTimeField(auto_now=False, blank=True, null=True)
    provider = models.ForeignKey('cla_provider.Provider', blank=True, null=True)
    notes = models.TextField(blank=True)
    provider_notes = models.TextField(blank=True)
    in_scope = models.NullBooleanField(default=None, null=True, blank=True)
    laa_reference = models.BigIntegerField(null=True, blank=True, unique=True)
    thirdparty_details = models.ForeignKey('ThirdPartyDetails', blank=True, null=True)
    adaptation_details = models.ForeignKey('AdaptationDetails', blank=True, null=True)


    def _set_reference_if_necessary(self):
        if not self.reference:
            # TODO make it better
            from django.utils.crypto import get_random_string
            self.reference = u'%s-%s-%s' % (
                get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
                get_random_string(length=4, allowed_chars='0123456789'),
                get_random_string(length=4, allowed_chars='0123456789')
            )

    def save(self, *args, **kwargs):
        self._set_reference_if_necessary()

        if not self.pk:
            super(Case, self).save(*args, **kwargs)
            self.laa_reference = self.pk + settings.LAA_REFERENCE_SEED
            kwargs['force_insert'] = False
            return self.save(*args, **kwargs)

        return super(Case, self).save(*args, **kwargs)

    def assign_to_provider(self, provider):
        self.provider = provider
        self.save()

    def associate_personal_details(self, ref):
        self.personal_details = PersonalDetails.objects.get(reference=ref)
        self.save()

    def associate_thirdparty_details(self, ref):
        self.thirdparty_details = ThirdPartyDetails.objects.get(reference=ref)
        self.save()

    def associate_adaptation_details(self, ref):
        self.adaptation_details = AdaptationDetails.objects.get(reference=ref)
	self.save()

    def associate_eligibility_check(self, ref):
        self.eligibility_check = EligibilityCheck.objects.get(reference=ref)
        self.save()

    def lock(self, user, save=True):
        if not self.locked_by:
            self.locked_by = user
            self.locked_at = datetime.datetime.utcnow().replace(tzinfo=utc)
            if save:
                self.save()
            return True
        else:
            if self.locked_by != user:
                logger.warning(u'User %s tried to lock case %s locked already by %s' % (
                    user, self.reference, self.locked_by
                ))

        return False

    def is_open(self):
        return self.state == CASE_STATES.OPEN

    def is_closed(self):
        return self.state == CASE_STATES.CLOSED

    def is_accepted(self):
        return self.state == CASE_STATES.ACCEPTED

    def _set_state(self, state):
        self.state = state
        self.save()
        return True

    def close(self):
        if not self.is_open() and not self.is_accepted():
            raise InvalidMutationException(
                u"Case should be 'OPEN' or 'ACCEPTED' to be closed but it's currently '%s'" % (
                    self.get_state_display()
                )
            )
        return self._set_state(CASE_STATES.CLOSED)

    def reject(self):
        if not self.is_open():
            raise InvalidMutationException(
                u"Case should be 'OPEN' to be rejected but it's currently '%s'" % (
                    self.get_state_display()
                )
            )

        self._set_state(CASE_STATES.REJECTED)

    def accept(self):
        if not self.is_open():
            raise InvalidMutationException(
                u"Case should be 'OPEN' to be accepted but it's currently '%s'" % (
                    self.get_state_display()
                )
            )

        self._set_state(CASE_STATES.ACCEPTED)


class CaseLogType(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    subtype = models.CharField(max_length=50)
    description = models.TextField()
    action_key = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return u'%s' % self.code

    class Meta:
        ordering = ['code']


class CaseLog(TimeStampedModel):
    case = models.ForeignKey(Case)
    logtype = models.ForeignKey(CaseLogType)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s' % (self.case, self.logtype)

    class Meta:
        ordering = ['-created']
