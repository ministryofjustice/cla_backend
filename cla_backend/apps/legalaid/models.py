from eligibility_calculator.models import CaseData
from uuidfield import UUIDField

from django.core.validators import MaxValueValidator
from django.db import models

from model_utils.models import TimeStampedModel

# from jsonfield import JSONField

from .constants import STATE_MAYBE, STATE_CHOICES


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
        if not self.you or not self.you.savings:
            raise ValueError("Can't do means test without specifying 'your savings' at a minimum.")

        d = {}
        d['facts'] = {}

        d['category'] = self.category.code
        d['dependant_children'] = self.dependants_old + self.dependants_young
        if self.you:
            d['you'] = {}

        if self.you.savings:
            savings = {}
            savings['savings'] = self.you.savings.bank_balance
            savings['investments'] = self.you.savings.investment_balance
            savings['money_owed']  = self.you.savings.credit_balance
            savings['valuable_items'] = self.your_finances.asset_balance
            d['you']['savings'] = savings

        if self.you.income:
            income = {}
            income['earnings'] = self.your_finances.earnings
            income['other_income'] = self.your_finances.other_income
            income['self_employed'] = self.your_finances.self_employed
            d['you']['income'] = income

        if self.you.deductions:
            deductions = {}
            deductions['income_tax_and_ni'] = self.you.deductions.income_tax_and_ni
            deductions['maintenance'] = self.you.deductions.maintenance
            deductions['mortgage_or_rent'] = self.you.deductions.mortgage_or_rent
            deductions['criminal_legalaid_contributions'] = self.you.deductions.criminal_legalaid_contributions
            d['you']['deductions'] = deductions

        d['facts']['has_partner'] = self.has_partner

        if self.has_partner:
            d['partner'] = {}
            if self.partner.savings:
                partner_savings = {}
                partner_savings['savings'] = self.partner_finances.bank_balance
                partner_savings['investments'] = self.partner_finances.investment_balance
                partner_savings['money_owed']  = self.partner_finances.credit_balance
                partner_savings['valuable_items'] = self.partner_finances.asset_balance
                d['partner']['savings'] = partner_savings

            if self.partner.income:
                partner_income = {}
                partner_income['earnings'] = self.partner_finances.earnings
                partner_income['other_income'] = self.partner_finances.other_income
                partner_income['self_employed'] = self.partner_finances.self_employed
                d['partner']['income'] = partner_income

        d['property_data'] = self.property_set.values_list('value', 'mortgage_left', 'share')
        d['is_you_or_your_partner_over_60'] = self.is_you_or_your_partner_over_60
        d['on_passported_benefits'] = self.on_passported_benefits

        # Fake
        d['is_partner_opponent'] = False

        return CaseData(**d)


class Property(TimeStampedModel):
    value = models.PositiveIntegerField(default=0)
    mortgage_left = models.PositiveIntegerField(default=0)
    share = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    eligibility_check = models.ForeignKey(EligibilityCheck)

    class Meta:
        verbose_name_plural = "properties"


class Case(TimeStampedModel):
    reference = models.CharField(max_length=128, unique=True, editable=False)
    eligibility_check = models.OneToOneField(EligibilityCheck)
    personal_details = models.ForeignKey(PersonalDetails)

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


# class Answer(TimeStampedModel):
#     question = models.ForeignKey(Question)
#     value = JSONField()
#     eligibility_check = models.ForeignKey(EligibilityCheck)
