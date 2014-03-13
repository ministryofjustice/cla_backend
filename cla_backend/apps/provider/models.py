from django.db import models
from model_utils.models import TimeStampedModel

class Provider(TimeStampedModel):
    name = models.CharField(max_length=255)
    opening_hours = models.CharField(max_length=100)
    law_category = models.ManyToManyField('legalaid.Category')
    active = models.BooleanField(default=False)

class Staff(TimeStampedModel):
    user = models.OneToOneField('auth.User')
    provider = models.ForeignKey(Provider)
    is_staff_superuser = models.BooleanField(default=False)

