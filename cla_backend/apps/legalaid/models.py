from eligibility_calculator.models import CaseData
from uuidfield import UUIDField

from django.core.validators import MaxValueValidator
from django.db import models

from model_utils.models import TimeStampedModel

# from jsonfield import JSONField

from .constants import STATE_MAYBE, STATE_CHOICES


class Category(TimeStampedModel):
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
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

    # need to be moved into graph/questions format soon
    is_you_or_your_partner_over_60 = models.BooleanField(default=False)
    has_partner = models.BooleanField(default=False)

    def to_case_data(self):
        return CaseData()


class Property(TimeStampedModel):
    value = models.PositiveIntegerField(default=0)
    equity = models.PositiveIntegerField(default=0)
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
