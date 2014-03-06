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


class Finance(TimeStampedModel):
    bank_balance = models.PositiveIntegerField(default=0)
    investment_balance = models.PositiveIntegerField(default=0)
    asset_balance = models.PositiveIntegerField(default=0)
    credit_balance = models.PositiveIntegerField(default=0)

    earnings = models.PositiveIntegerField(default=0)
    other_income = models.PositiveIntegerField(default=0)
    self_employed = models.BooleanField(default=False)

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


# class Person():
#     income = fk
#     savings = fk
#     deductions = fk


class EligibilityCheck(TimeStampedModel):
    reference = UUIDField(auto=True, unique=True)

    category = models.ForeignKey(Category, blank=True, null=True)
    your_finances = models.ForeignKey(Finance, blank=True, null=True, related_name='your_savings')
    partner_finances = models.ForeignKey(Finance, blank=True, null=True, related_name='partner_savings')
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
        if not self.your_finances:
            raise ValueError("Can't do means test without specifying 'your_finances' at a minimum.")

        d = {}
        d['category'] = self.category.code
        d['dependant_children'] = self.dependants_old + self.dependants_young
        d['savings'] = self.your_finances.bank_balance
        d['investments'] = self.your_finances.investment_balance
        d['money_owed']  = self.your_finances.credit_balance
        d['valuable_items'] = self.your_finances.asset_balance
        d['earnings'] = self.your_finances.earnings
        d['other_income'] = self.your_finances.other_income
        d['self_employed'] = self.your_finances.self_employed

        d['income_tax_and_ni'] = self.your_finances.income_tax_and_ni
        d['maintenance'] = self.your_finances.maintenance
        d['mortgage_or_rent'] = self.your_finances.mortgage_or_rent
        d['criminal_legalaid_contributions'] = self.your_finances.criminal_legalaid_contributions

        d['has_partner'] = self.has_partner

        if self.has_partner:
            d['partner_savings'] = self.partner_finances.bank_balance
            d['partner_investments'] = self.partner_finances.investment_balance
            d['partner_money_owed']  = self.partner_finances.credit_balance
            d['partner_valuable_items'] = self.partner_finances.asset_balance
            d['partner_earnings'] = self.partner_finances.earnings
            d['partner_other_income'] = self.partner_finances.other_income
            d['partner_self_employed'] = self.partner_finances.self_employed

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
