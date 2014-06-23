import logging
import datetime
import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from django.conf import settings
from django.db.models import F
from django.utils.timezone import utc

from eligibility_calculator.models import CaseData
from uuidfield import UUIDField

from model_utils.models import TimeStampedModel

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


# class Question(TimeStampedModel):
#     name = models.CharField(max_length=500)
#     description = models.TextField(blank=True)
#     guidance = models.TextField(blank=True)
#     config = JSONField(blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ['order']

#     def __unicode__(self):
#         return u'%s' % self.name


class Savings(TimeStampedModel):
    bank_balance = MoneyField(default=0)
    investment_balance = MoneyField(default=0)
    asset_balance = MoneyField(default=0)
    credit_balance = MoneyField(default=0)


class Income(TimeStampedModel):
    earnings = MoneyIntervalField()
    other_income = MoneyIntervalField()
    self_employed = models.BooleanField(default=False)


class Deductions(TimeStampedModel):
    income_tax = MoneyIntervalField()
    national_insurance = MoneyIntervalField()
    maintenance = MoneyIntervalField()
    childcare = MoneyIntervalField()
    mortgage = MoneyIntervalField()
    rent = MoneyIntervalField()
    criminal_legalaid_contributions = MoneyField(default=0)


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
    language = models.CharField(max_length=30, choices=ADAPTATION_LANGUAGES)
    notes = models.TextField(blank=True)
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


class EligibilityCheck(TimeStampedModel):
    reference = UUIDField(auto=True, unique=True)

    category = models.ForeignKey(Category, blank=True, null=True)
    you = models.ForeignKey(Person, blank=True, null=True, related_name='you')
    partner = models.ForeignKey(Person, blank=True, null=True, related_name='partner')
    your_problem_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    state = models.CharField(
        max_length=50, default=ELIGIBILITY_STATES.MAYBE,
        choices=ELIGIBILITY_STATES.CHOICES
    )
    dependants_young = models.PositiveIntegerField(default=0)
    dependants_old = models.PositiveIntegerField(default=0)
    on_passported_benefits = models.BooleanField(default=False)
    on_nass_benefits = models.BooleanField(default=False)


    # need to be moved into graph/questions format soon
    is_you_or_your_partner_over_60 = models.BooleanField(default=False)
    has_partner = models.BooleanField(default=False)

    def to_case_data(self):
        d = {}

        if self.category:
            d['category'] = self.category.code

        d['property_data'] = self.property_set.values_list(
            'value', 'mortgage_left', 'share', 'disputed'
        )

        d['facts'] = {}
        d['facts']['dependant_children'] = self.dependants_old + self.dependants_young
        d['facts']['has_partner'] = self.has_partner
        d['facts']['is_you_or_your_partner_over_60'] = self.is_you_or_your_partner_over_60
        d['facts']['on_passported_benefits'] = self.on_passported_benefits
        d['facts']['on_nass_benefits'] = self.on_nass_benefits

        d['you'] = {}
        if self.you:
            if self.you.savings:
                savings = {}
                savings['bank_balance'] = self.you.savings.bank_balance
                savings['investment_balance'] = self.you.savings.investment_balance
                savings['credit_balance']  = self.you.savings.credit_balance
                savings['asset_balance'] = self.you.savings.asset_balance
                d['you']['savings'] = savings

            if self.you.income:
                income = {}
                income['earnings'] = self.you.income.earnings.as_monthly()
                income['other_income'] = self.you.income.other_income.as_monthly()
                income['self_employed'] = self.you.income.self_employed or False
                d['you']['income'] = income

            if self.you.deductions:
                deductions = {}
                deductions['income_tax'] = self.you.deductions.income_tax.as_monthly()
                deductions['national_insurance']  = self.you.deductions.national_insurance.as_monthly()
                deductions['maintenance'] = self.you.deductions.maintenance.as_monthly()
                deductions['childcare'] = self.you.deductions.childcare.as_monthly()
                deductions['mortgage'] = self.you.deductions.mortgage.as_monthly()
                deductions['rent'] = self.you.deductions.rent.as_monthly()
                deductions['criminal_legalaid_contributions'] = self.you.deductions.criminal_legalaid_contributions
                d['you']['deductions'] = deductions

        if self.has_partner:
            d['partner'] = {}
            if self.partner:
                if self.partner.savings:
                    partner_savings = {}
                    partner_savings['bank_balance'] = self.partner.savings.bank_balance
                    partner_savings['investment_balance'] = self.partner.savings.investment_balance
                    partner_savings['credit_balance']  = self.partner.savings.credit_balance
                    partner_savings['asset_balance'] = self.partner.savings.asset_balance
                    d['partner']['savings'] = partner_savings

                if self.partner.income:
                    partner_income = {}
                    partner_income['earnings'] = self.partner.income.earnings.as_monthly()
                    partner_income['other_income'] = self.partner.income.other_income.as_monthly()
                    partner_income['self_employed'] = self.partner.income.self_employed
                    d['partner']['income'] = partner_income

                if self.partner.deductions:
                    partner_deductions = {}
                    partner_deductions['income_tax'] = self.partner.deductions.income_tax.as_monthly()
                    partner_deductions['national_insurance']  = self.partner.deductions.national_insurance.as_monthly()
                    partner_deductions['maintenance'] = self.partner.deductions.maintenance.as_monthly()
                    partner_deductions['childcare'] = self.partner.deductions.childcare.as_monthly()
                    partner_deductions['mortgage'] = self.partner.deductions.mortgage.as_monthly()
                    partner_deductions['rent'] = self.partner.deductions.rent.as_monthly()
                    partner_deductions['criminal_legalaid_contributions'] = self.partner.deductions.criminal_legalaid_contributions
                    d['partner']['deductions'] = partner_deductions

        # Fake
        d['facts']['is_partner_opponent'] = False

        return CaseData(**d)


class Property(TimeStampedModel):
    value = MoneyField(default=0)
    mortgage_left = MoneyField(default=0)
    share = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    eligibility_check = models.ForeignKey(EligibilityCheck)
    disputed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "properties"


# class OutcomeCode(TimeStampedModel):
#     code = models.CharField(max_length=50, unique=True)
#     description = models.TextField()
#     case_state = models.PositiveSmallIntegerField(
#         choices=CASE_STATES.CHOICES, null=True, blank=True
#     )
#
#     def __unicode__(self):
#         return u'%s' % self.code
#
#     class Meta:
#         ordering = ['code']


class Case(TimeStampedModel):
    reference = models.CharField(max_length=128, unique=True, editable=False)
    eligibility_check = models.OneToOneField(EligibilityCheck)
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
