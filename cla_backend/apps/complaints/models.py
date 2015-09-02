# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from model_utils.models import TimeStampedModel
from cla_eventlog.constants import LOG_LEVELS
from complaints.constants import COMPLAINT_SOURCE, SLA_DAYS, \
    HOLDING_LETTER_SLA_DAYS
from legalaid.utils.sla import get_day_sla_time


class ComplaintManager(models.Manager):
    def get_queryset(self):
        return super(ComplaintManager, self).get_queryset().select_related(
            'eod',
            'eod__case',
            'eod__case__personal_details',
            'eod__case__eligibility_check',
            'eod__case__eligibility_check__category',
            'category',
        ).prefetch_related(
            'eod__categories',
        )


class Complaint(TimeStampedModel):
    eod = models.ForeignKey('legalaid.EODDetails')

    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=15, choices=COMPLAINT_SOURCE,
                              blank=True)
    level = models.PositiveSmallIntegerField(
        choices=((LOG_LEVELS.HIGH, 'Major'), (LOG_LEVELS.MINOR, 'Minor')),
        default=LOG_LEVELS.MINOR
    )
    justified = models.NullBooleanField()
    resolved = models.NullBooleanField()
    category = models.ForeignKey('Category', blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(app_label)s_%(class)s_owner',
        limit_choices_to={'operator__is_manager': True},
        blank=True,
        null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(app_label)s_%(class)s_created_by',
        limit_choices_to={'operator__isnull': False},
        blank=True,
        null=True)

    logs = GenericRelation('cla_eventlog.ComplaintLog',
                           related_query_name='complaint')

    objects = ComplaintManager()

    class Meta(object):
        ordering = ('-created',)

    def __init__(self, *args, **kwargs):
        self._closed = NotImplemented
        self._holding_letter = NotImplemented
        self._full_letter = NotImplemented
        super(Complaint, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'Complaint on case %s' % self.eod.case

    @property
    def case(self):
        return self.eod.case

    @property
    def status_label(self):
        if self.resolved is not None:
            return 'resolved' if self.resolved else 'unresolved'
        if self.owner_id:
            return 'pending'
        return 'received'

    @property
    def closed(self):
        """
        The date the complaint was closed if it has a closed event log
        NB: Not loaded here if this model is being serialised in a complaint
            view set
        """
        if self._closed is NotImplemented:
            last_closed = self.logs.filter(code='COMPLAINT_CLOSED').order_by('-created').first()
            self._closed = last_closed.created if last_closed else None
        return self._closed

    @closed.setter
    def closed(self, value):
        self._closed = value

    @property
    def holding_letter(self):
        """
        The date the latest holding letter was sent
        NB: Not loaded here if this model is being serialised in a complaint
            view set
        """
        if self._holding_letter is NotImplemented:
            last_closed = self.logs.filter(code='HOLDING_LETTER_SENT').order_by('-created').first()
            self._holding_letter = last_closed.created if last_closed else None
        return self._holding_letter

    @holding_letter.setter
    def holding_letter(self, value):
        self._holding_letter = value

    @property
    def full_letter(self):
        """
        The date the latest full response was sent
        NB: Not loaded here if this model is being serialised in a complaint
            view set
        """
        if self._full_letter is NotImplemented:
            last_closed = self.logs.filter(code='FULL_RESPONSE_SENT').order_by('-created').first()
            self._full_letter = last_closed.created if last_closed else None
        return self._full_letter

    @full_letter.setter
    def full_letter(self, value):
        self._full_letter = value

    @property
    def out_of_sla(self):
        """
        True if complaint is unresolved for over 15 working days.
        """
        sla = get_day_sla_time(self.created, SLA_DAYS)
        return self.closed is None and timezone.now() > sla

    @property
    def holding_letter_out_of_sla(self):
        """
        True if holding letter is not sent within 1 working day.
        """
        holding_sla = get_day_sla_time(self.created, HOLDING_LETTER_SLA_DAYS)
        return self.holding_letter is None and timezone.now() > holding_sla

    def requires_action_at(self):
        if self.holding_letter is None:
            return get_day_sla_time(self.created, HOLDING_LETTER_SLA_DAYS)
        elif self.closed is None:
            return get_day_sla_time(self.created, SLA_DAYS)


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.name
