from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel


class ProviderManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(active=True)


class Provider(TimeStampedModel):
    name = models.CharField(max_length=255)
    opening_hours = models.CharField(max_length=100)
    law_category = models.ManyToManyField('legalaid.Category',
                                          through='ProviderAllocation')
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
    weighted_distribution = models.FloatField()  # see XXXXXXXXXXXX

    objects = ProviderAllocationManager()

    def __unicode__(self):
        return u'%s provides %s' % (self.provider, self.category)


class Staff(TimeStampedModel):
    user = models.OneToOneField('auth.User')
    provider = models.ForeignKey(Provider)
    is_staff_superuser = models.BooleanField(default=False)


class OutOfHoursRota(TimeStampedModel):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    category = models.ForeignKey('legalaid.Category')
    provider = models.ForeignKey(Provider)

    def __unicode__(self):
        return u'%s provides out of hours service for %s between %s - %s' \
               % (
            self.provider,
            self.category.code,
            self.start_date,
            self.end_date
        )

    def clean(self):

        if not self.end_date > self.start_date:
            raise ValidationError("End date must be after start date.")

        # make sure you can't set a category that a provider
        # is not able to provide.
        if self.category not in self.provider.law_category.all():
            raise ValidationError(
                _(u"Provider {provider} doesn't offer help for {category}") \
                .format(provider=self.provider, category=self.category))

        overlapping = self.__class__._default_manager.filter(
            Q(start_date__range=[self.start_date, self.end_date]) |
            Q(end_date__range=[self.start_date, self.end_date]),
            provider=self.provider,
            category=self.category,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping:
            raise ValidationError(
                _(u"Overlapping rota allocation not allowed"))