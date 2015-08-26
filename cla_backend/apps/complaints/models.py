# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from model_utils.models import TimeStampedModel
from cla_eventlog.constants import LOG_LEVELS
from complaints.constants import COMPLAINT_SOURCE


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
        choices=tuple(filter(lambda (level, desc): level != 21, LOG_LEVELS.CHOICES)),
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
    def out_of_sla(self):
        """
        True if complaint is unresolved for over 15 days.
        """
        return (self.closed or timezone.now()) - self.created > datetime.timedelta(days=15)


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.name
