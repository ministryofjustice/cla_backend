# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

from model_utils.models import TimeStampedModel
from complaints.constants import COMPLAINT_SOURCE


class Complaint(TimeStampedModel):
    case = models.ForeignKey('legalaid.Case')
    eod = models.ForeignKey('legalaid.EODDetails', null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True,
                                   null=True)

    source = models.CharField(max_length=15, choices=COMPLAINT_SOURCE)


