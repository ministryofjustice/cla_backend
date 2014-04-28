import logging
import datetime

from django.core.validators import MaxValueValidator
from django.db import models
from django.conf import settings
from django.utils.timezone import utc

from eligibility_calculator.models import CaseData
from uuidfield import UUIDField

from model_utils.models import TimeStampedModel

# from jsonfield import JSONField

from cla_common.constants import STATE_MAYBE, \
    STATE_CHOICES, CASE_STATE_CHOICES, CASE_STATE_OPEN, CASE_STATE_CLOSED, \
    CASE_STATE_REJECTED, CASE_STATE_ACCEPTED


from legalaid.exceptions import InvalidMutationException

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
    bank_balance = models.PositiveIntegerField(default=0)
    investment_balance = models.PositiveIntegerField(default=0)
    asset_balance = models.PositiveIntegerField(default=0)
    credit_balance = models.PositiveIntegerField(default=0)


class Income(TimeStampedModel):
    earnings = models.PositiveIntegerField(default=0)
    other_income = models.PositiveIntegerField(default=0)
    self_employed = models.BooleanField(default=False)


class Deductions(TimeStampedModel):
    income_tax_and_ni = models.PositiveIntegerField(default=0)
    maintenance = models.PositiveIntegerField(default=0)
    childcare = models.PositiveIntegerField(default=0)
    mortgage_or_rent = models.PositiveIntegerField(default=0)
    criminal_legalaid_contributions = models.PositiveIntegerField(default=0)


class PersonalDetails(TimeStampedModel):
    title = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=400)
    postcode = models.CharField(max_length=12)
    street = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    mobile_phone = models.CharField(max_length=20, blank=True)
    home_phone = models.CharField(max_length=20, blank=True)
    # email = models.EmailField(blank=True)

    class Meta:
        verbose_name_plural = "personal details"


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
    state = models.PositiveSmallIntegerField(default=STATE_MAYBE, choices=STATE_CHOICES)
    dependants_young = models.PositiveIntegerField(default=0)
    dependants_old = models.PositiveIntegerField(default=0)
    on_passported_benefits = models.BooleanField(default=False)


    # need to be moved into graph/questions format soon
    is_you_or_your_partner_over_60 = models.BooleanField(default=False)
    has_partner = models.BooleanField(default=False)

    def to_case_data(self):
        d = {}

        if self.category:
            d['category'] = self.category.code

        d['property_data'] = self.property_set.values_list('value', 'mortgage_left', 'share')

        d['facts'] = {}
        d['facts']['dependant_children'] = self.dependants_old + self.dependants_young
        d['facts']['has_partner'] = self.has_partner
        d['facts']['is_you_or_your_partner_over_60'] = self.is_you_or_your_partner_over_60
        d['facts']['on_passported_benefits'] = self.on_passported_benefits

        d['you'] = {}
        if self.you:
            if self.you.savings:
                savings = {}
                savings['savings'] = self.you.savings.bank_balance
                savings['investments'] = self.you.savings.investment_balance
                savings['money_owed']  = self.you.savings.credit_balance
                savings['valuable_items'] = self.you.savings.asset_balance
                d['you']['savings'] = savings

            if self.you.income:
                income = {}
                income['earnings'] = self.you.income.earnings
                income['other_income'] = self.you.income.other_income
                income['self_employed'] = self.you.income.self_employed or False
                d['you']['income'] = income

            if self.you.deductions:
                deductions = {}
                deductions['income_tax_and_ni'] = self.you.deductions.income_tax_and_ni
                deductions['maintenance'] = self.you.deductions.maintenance
                deductions['childcare'] = self.you.deductions.childcare
                deductions['mortgage_or_rent'] = self.you.deductions.mortgage_or_rent
                deductions['criminal_legalaid_contributions'] = self.you.deductions.criminal_legalaid_contributions
                d['you']['deductions'] = deductions

        if self.has_partner:
            d['partner'] = {}
            if self.partner.savings:
                partner_savings = {}
                partner_savings['savings'] = self.partner.savings.bank_balance
                partner_savings['investments'] = self.partner.savings.investment_balance
                partner_savings['money_owed']  = self.partner.savings.credit_balance
                partner_savings['valuable_items'] = self.partner.savings.asset_balance
                d['partner']['savings'] = partner_savings

            if self.partner.income:
                partner_income = {}
                partner_income['earnings'] = self.partner.income.earnings
                partner_income['other_income'] = self.partner.income.other_income
                partner_income['self_employed'] = self.partner.income.self_employed
                d['partner']['income'] = partner_income

            if self.partner.deductions:
                partner_deductions = {}
                partner_deductions['income_tax_and_ni'] = self.partner.deductions.income_tax_and_ni
                partner_deductions['maintenance'] = self.partner.deductions.maintenance
                partner_deductions['childcare'] = self.partner.deductions.childcare
                partner_deductions['mortgage_or_rent'] = self.partner.deductions.mortgage_or_rent
                partner_deductions['criminal_legalaid_contributions'] = self.partner.deductions.criminal_legalaid_contributions
                d['partner']['deductions'] = partner_deductions

        # Fake
        d['facts']['is_partner_opponent'] = False

        return CaseData(**d)


class Property(TimeStampedModel):
    value = models.PositiveIntegerField(default=0)
    mortgage_left = models.PositiveIntegerField(default=0)
    share = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    eligibility_check = models.ForeignKey(EligibilityCheck)

    class Meta:
        verbose_name_plural = "properties"


class OutcomeCode(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    case_state = models.PositiveSmallIntegerField(
        choices=CASE_STATE_CHOICES, null=True, blank=True
    )

    def __unicode__(self):
        return u'%s' % self.code

    class Meta:
        ordering = ['code']


class Case(TimeStampedModel):
    reference = models.CharField(max_length=128, unique=True, editable=False)
    eligibility_check = models.OneToOneField(EligibilityCheck)
    personal_details = models.ForeignKey(PersonalDetails, blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    state = models.PositiveSmallIntegerField(choices=CASE_STATE_CHOICES, default=CASE_STATE_OPEN)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        related_name='case_locked'
    )
    locked_at = models.DateTimeField(auto_now=False, blank=True, null=True)
    provider = models.ForeignKey('cla_provider.Provider', blank=True, null=True)
    notes = models.TextField(blank=True)
    provider_notes = models.TextField(blank=True)

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
        return super(Case, self).save(*args, **kwargs)

    def assign_to_provider(self, provider):
        self.provider = provider
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
        return self.state == CASE_STATE_OPEN

    def is_closed(self):
        return self.state == CASE_STATE_CLOSED

    def is_accepted(self):
        return self.state == CASE_STATE_ACCEPTED

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
        return self._set_state(CASE_STATE_CLOSED)

    def reject(self):
        if not self.is_open():
            raise InvalidMutationException(
                u"Case should be 'OPEN' to be rejected but it's currently '%s'" % (
                    self.get_state_display()
                )
            )

        self._set_state(CASE_STATE_REJECTED)

    def accept(self):
        if not self.is_open():
            raise InvalidMutationException(
                u"Case should be 'OPEN' to be accepted but it's currently '%s'" % (
                    self.get_state_display()
                )
            )

        self._set_state(CASE_STATE_ACCEPTED)


class CaseOutcome(TimeStampedModel):
    case = models.ForeignKey(Case)
    outcome_code = models.ForeignKey(OutcomeCode)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    notes = models.TextField()

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%s - %s' % (self.case, self.outcome_code)


# class Answer(TimeStampedModel):
#     question = models.ForeignKey(Question)
#     value = JSONField()
#     eligibility_check = models.ForeignKey(EligibilityCheck)
