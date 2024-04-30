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
from .constants import DEFAULT_WORKING_DAYS
from datetime import datetime


def random_uuid_str():
    return str(uuid.uuid4())


class ProviderManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(active=True)


class Provider(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
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


class WorkingDays(models.Model):
    """
    This model represents the working days for Education specialist providers, to align with the changes required as part of LGA-2904.
    """

    provider_allocation = models.OneToOneField("ProviderAllocation")
    monday = models.BooleanField(default=DEFAULT_WORKING_DAYS["monday"])
    tuesday = models.BooleanField(default=DEFAULT_WORKING_DAYS["tuesday"])
    wednesday = models.BooleanField(default=DEFAULT_WORKING_DAYS["wednesday"])
    thursday = models.BooleanField(default=DEFAULT_WORKING_DAYS["thursday"])
    friday = models.BooleanField(default=DEFAULT_WORKING_DAYS["friday"])
    saturday = models.BooleanField(default=DEFAULT_WORKING_DAYS["saturday"])
    sunday = models.BooleanField(default=DEFAULT_WORKING_DAYS["sunday"])

    class Meta:
        verbose_name = "Working Days"
        verbose_name_plural = "Working Days"

    def is_working_today(self):
        """ Returns if the provider allocation is allocated to work today.s

        Returns:
            Boolean: Is the provider working today
        """
        current_day = get_current_day_as_string()

        return self.is_working_on_day(current_day)

    def is_working_on_day(self, day):
        """ Takes in a day of the week as a string and returns if the provider works on that day

        Args:
            day (str): Day of the week as a string. E.g. "Monday"

        Returns:
            Boolean: Is the provider working on the given day, will return None if the day is invalid
        """
        week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day = day.lower()
        if day not in week:
            return None

        return self.__getattribute__(day)

    @property
    def working_days_list(self):
        """Property containing a list of all the weekdays the provider allocation is working

        Returns:
            List[str]: A list of lower case weekday strings
        """
        week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        working_days = [day for day in week if self.is_working_on_day(day)]

        return working_days

    def __unicode__(self):
        return ""


def get_current_day_as_string():
    """ Returns the current day of the week as a lower case string.
    """
    week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_index = datetime.now().weekday()

    return week[day_index]


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

    def is_working_today(self):
        """Returns if the provider is working today, based on the WorkingDays model

        Returns:
            Boolean: Is the provider working today
        """
        current_day = get_current_day_as_string()

        if not hasattr(self, "workingdays"):
            return DEFAULT_WORKING_DAYS[current_day]

        return self.workingdays.is_working_today()

    @property
    def working_days(self):
        """Property containing a list of all the weekdays the provider allocation is working

        Returns:
            List[str]: A list of lower case weekday strings
        """
        if not hasattr(self, "workingdays"):
            working_day_list = []
            for day, is_working in DEFAULT_WORKING_DAYS.iteritems():
                if is_working:
                    working_day_list.append(day)
            return working_day_list

        return self.workingdays.working_days_list

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
        verbose_name_plural = "staff"

    def __unicode__(self):
        return self.user.username

    def is_unique_chs_user(self):
        return not bool(
            Staff.objects.filter(chs_organisation=self.chs_organisation, chs_user=self.chs_user)
            .exclude(pk=self.pk)
            .count()
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.chs_organisation = self.chs_organisation or random_uuid_str()
            self.chs_user = self.chs_user or random_uuid_str()

        # You are probably wondering why we don't use Meta.unique_together?
        # When DRF finds a model that has Meta.unique_together it will add a
        # rest_framework.validators.UniqueTogetherValidator to the serializer and it will enforce that uniqueness
        # even if user does not provide those fields(even when the field is marked as required=False)
        assert self.is_unique_chs_user(), "chs_user and chs_organisation must be unique when combined"
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
    class Analytics:
        _allow_analytics = True

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
