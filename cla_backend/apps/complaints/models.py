# -*- coding: utf-8 -*-
from django.conf import settings
from cla_eventlog.constants import LOG_LEVELS
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel
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
    source = models.CharField(max_length=15, choices=COMPLAINT_SOURCE)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS.CHOICES)
    justified = models.NullBooleanField()
    category = models.ForeignKey('Category')

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

    def __unicode__(self):
        return u'Complaint on case %s' % self.eod.case

    @property
    def case(self):
        return self.eod.case


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return self.name
