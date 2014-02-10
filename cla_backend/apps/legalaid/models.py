from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from model_utils.models import TimeStampedModel
from jsonfield import JSONField


STATE_CHOICES = (
    (0, 'Maybe'),
    (1, 'Yes'),
    (2, 'No'),
)

class Category(TimeStampedModel):
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Question(TimeStampedModel):
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    guidance = models.TextField(blank=True)
    config = JSONField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Savings(TimeStampedModel):
    bank_balance = models.PositiveIntegerField(default=0)
    investment_balance = models.PositiveIntegerField(default=0)
    asset_balance = models.PositiveIntegerField(default=0)
    credit_balance = models.PositiveIntegerField(default=0)



class PersonalDetails(TimeStampedModel):
    title = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=400)
    postcode = models.CharField(max_length=12)
    street = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    mobile_phone = models.CharField(max_length=20, blank=True)
    home_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

class EligibilityCheck(TimeStampedModel):
    category = models.ForeignKey(Category)
    your_savings = models.ForeignKey(Savings, related_name='your_savings')
    partner_savings = models.ForeignKey(Savings, blank=True, null=True, related_name='partner_savings')
    notes = models.TextField(blank=True)
    state = models.PositiveSmallIntegerField(default=0, choices=STATE_CHOICES)

class Property(TimeStampedModel):
    value = models.PositiveIntegerField(default=0)
    equity = models.PositiveIntegerField(default=0)
    share = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    eligibility_check = models.ForeignKey(EligibilityCheck)

class Case(TimeStampedModel):
    reference = models.CharField(max_length=128, unique=True)
    eligibility_check = models.ForeignKey(EligibilityCheck)
    personal_details = models.ForeignKey(PersonalDetails)




class Answer(TimeStampedModel):
    question = models.ForeignKey(Question)
    value = JSONField()
    eligibility_check = models.ForeignKey(EligibilityCheck)
