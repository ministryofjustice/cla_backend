from datetime import timedelta
import uuid

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save, pre_save

from jsonfield import JSONField
from model_utils.models import TimeStampedModel
from uuidfield import UUIDField

from core.validators import validate_first_of_month
from cla_common.constants import FEEDBACK_ISSUE
from .signals import log_staff_created, log_staff_modified


def random_uuid_str():
    return str(uuid.uuid4())


class ProviderManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(active=True)


class Provider(TimeStampedModel):
    name = models.CharField(max_length=255)
    opening_hours = models.CharField(max_length=100, blank=True)
    law_category = models.ManyToManyField("legalaid.Category", through="ProviderAllocation")
    active = models.BooleanField(default=False)
    short_code = models.CharField(max_length=100, blank=True)
    telephone_frontdoor = models.CharField(max_length=100, blank=True)
    telephone_backdoor = models.CharField(max_length=100, blank=True)

    email_address = models.EmailField(blank=True)

    objects = ProviderManager()

    def __unicode__(self):
        return u"%s" % self.name


class ProviderAllocationManager(models.Manager):
    def has_category(self, category):
        """
        @param category: type legalaid.Category
        """
        return self.get_queryset().filter(category=category)


class ProviderAllocation(TimeStampedModel):
    provider = models.ForeignKey(Provider)
    category = models.ForeignKey("legalaid.Category")
    weighted_distribution = models.FloatField()  # see XXXXXXXXXXXX

    objects = ProviderAllocationManager()

    def __unicode__(self):
        return u"%s provides %s" % (self.provider, self.category)


class ProviderPreAllocationManager(models.Manager):
    def get_queryset(self):
        super(ProviderPreAllocationManager, self).get_queryset().filter(
            created__lte=timezone.now() - timedelta(seconds=60)
        ).delete()

        return super(ProviderPreAllocationManager, self).get_queryset()

    def pre_allocate(self, category, provider, case):
        self.get_queryset().filter(case=case).delete()
        if not case.provider:
            self.get_queryset().create(category=category, provider=provider, case=case)

    def clear(self, case=None):
        qs = self.get_queryset()
        if case:
            qs = qs.filter(case=case)
        qs.delete()


class ProviderPreAllocation(TimeStampedModel):
    provider = models.ForeignKey(Provider)
    category = models.ForeignKey("legalaid.Category")
    case = models.ForeignKey("legalaid.Case")

    objects = ProviderPreAllocationManager()


class Staff(TimeStampedModel):
    user = models.OneToOneField("auth.User")
    provider = models.ForeignKey(Provider)
    is_manager = models.BooleanField(default=False)

    chs_organisation = models.CharField(
        max_length=500,
        help_text="Fake field to mirror old CHS extract, user can set this to whatever they like",
        blank=True,
        null=True,
    )
    chs_user = models.CharField(
        max_length=500,
        help_text="Fake field to mirror old CHS extract, user can set this to whatever they like",
        blank=True,
        null=True,
    )
    chs_password = models.CharField(
        max_length=500,
        help_text="Fake field to mirror old CHS extract, user can set this to whatever they like",
        blank=True,
        null=True,
    )

    def set_chs_password(self, raw_password):
        self.chs_password = make_password(raw_password)

    class Meta(object):
        unique_together = (("chs_organisation", "chs_user"),)
        verbose_name_plural = "staff"

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.pk:
            self.chs_organisation = self.chs_organisation or random_uuid_str()
            self.chs_user = self.chs_user or random_uuid_str()
        return super(Staff, self).save(*args, **kwargs)


class OutOfHoursRotaManager(models.Manager):
    def get_current(self, category, as_of=None):
        if not as_of:
            as_of = timezone.localtime(timezone.now())

        return self.get_queryset().get(category=category, start_date__lte=as_of, end_date__gte=as_of)


class OutOfHoursRota(TimeStampedModel):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    category = models.ForeignKey("legalaid.Category")
    provider = models.ForeignKey(Provider)

    objects = OutOfHoursRotaManager()

    def __unicode__(self):
        return u"%s provides out of hours service for %s between %s - %s" % (
            self.provider,
            self.category.code,
            self.start_date,
            self.end_date,
        )

    def clean(self):
        if not self.end_date > self.start_date:
            raise ValidationError("End date must be after start date.")

        # make sure you can't set a category that a provider
        # is not able to provide.
        if self.category not in self.provider.law_category.all():
            raise ValidationError(
                _(u"Provider {provider} doesn't offer help for {category}").format(
                    provider=self.provider, category=self.category
                )
            )

        start_range = Q(start_date__range=[self.start_date, self.end_date])
        end_range = Q(end_date__range=[self.start_date, self.end_date])
        overlapping = self.__class__._default_manager.filter(start_range | end_range, category=self.category)
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping:
            raise ValidationError(_(u"Overlapping rota allocation not allowed"))


class Feedback(TimeStampedModel):
    reference = UUIDField(auto=True, unique=True)
    case = models.ForeignKey("legalaid.Case", related_name="provider_feedback")

    created_by = models.ForeignKey(Staff)
    comment = models.TextField()

    justified = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    issue = models.CharField(choices=FEEDBACK_ISSUE, max_length=100)


class CSVUpload(TimeStampedModel):

    provider = models.ForeignKey(Provider)
    created_by = models.ForeignKey(Staff)
    comment = models.TextField(blank=True, null=True)
    body = JSONField()
    month = models.DateField(validators=[validate_first_of_month])

    class Meta(object):
        unique_together = [["provider", "month"]]


post_save.connect(log_staff_created, sender=Staff)
pre_save.connect(log_staff_modified, sender=Staff)
