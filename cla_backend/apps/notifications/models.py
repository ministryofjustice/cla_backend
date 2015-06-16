# -*- coding: utf-8 -*-
from django.utils import timezone
from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel

from .constants import NOTIFICATION_TYPES


class NotificationManager(models.Manager):
    def live(self):
        now = timezone.now()
        return self.get_queryset().filter(
            start_time__lt=now,
            end_time__gt=now
        )


class Notification(TimeStampedModel):
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    notification = models.CharField(max_length=100)
    description = models.CharField(max_length=600)
    notes = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = NotificationManager()
