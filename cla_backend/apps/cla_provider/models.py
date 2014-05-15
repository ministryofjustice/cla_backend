from django.db import models

from model_utils.models import TimeStampedModel


class ProviderManager(models.Manager):

    def active(self):
        return self.get_queryset().filter(active=True)


class Provider(TimeStampedModel):
    name = models.CharField(max_length=255)
    opening_hours = models.CharField(max_length=100)
    law_category = models.ManyToManyField('legalaid.Category', through='ProviderAllocation')
    active = models.BooleanField(default=False)
    short_code = models.CharField(max_length=100, blank=True)
    telephone_frontdoor = models.CharField(max_length=100, blank=True)
    telephone_backdoor = models.CharField(max_length=100, blank=True)

    objects = ProviderManager()

    def __unicode__(self):
        return u'%s' % self.name


class ProviderAllocationManager(models.Manager):

    def has_category(self, category):
        """
        @param category: type legalaid.Category
        """
        return self.get_queryset().filter(category=category)


class ProviderAllocation(TimeStampedModel):
    provider = models.ForeignKey(Provider)
    category = models.ForeignKey('legalaid.Category')
    weighted_distribution = models.FloatField() # see XXXXXXXXXXXX

    objects = ProviderAllocationManager()

    def __unicode__(self):
        return u'%s provides %s' % (self.provider, self.category)


class Staff(TimeStampedModel):
    user = models.OneToOneField('auth.User')
    provider = models.ForeignKey(Provider)
    is_staff_superuser = models.BooleanField(default=False)
