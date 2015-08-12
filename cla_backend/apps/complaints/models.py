# -*- coding: utf-8 -*-
from cla_common.constants import REQUIRES_ACTION_BY
from django.conf import settings
from cla_eventlog.constants import LOG_LEVELS
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils.models import TimeStampedModel
from complaints.constants import COMPLAINT_SOURCE


class Complaint(TimeStampedModel):
    case = models.ForeignKey('legalaid.Case')
    eod = models.ForeignKey('legalaid.EODDetails')

    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=15, choices=COMPLAINT_SOURCE.CHOICES)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS.CHOICES)
    category = models.ForeignKey('Category')

    requires_action_by = models.CharField(
        max_length=50, choices=REQUIRES_ACTION_BY.CHOICES,
        default=REQUIRES_ACTION_BY.OPERATOR,
        blank=True, null=True, editable=False
    )

    logs = GenericRelation('cla_eventlog.ComplaintLog',
                           related_query_name='complaint')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                   null=True)


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)




