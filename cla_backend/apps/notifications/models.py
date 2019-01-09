# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from model_utils.models import TimeStampedModel

from .constants import NOTIFICATION_TYPES
from .signals import send_notifications_to_users


class NotificationManager(models.Manager):
    def live(self):
        now = timezone.now()
        return self.get_queryset().filter(start_time__lt=now, end_time__gt=now)


class Notification(TimeStampedModel):
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="notification")
    notification = models.CharField(max_length=100)
    description = models.CharField(max_length=600, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = NotificationManager()


post_save.connect(send_notifications_to_users, sender=Notification)
post_delete.connect(send_notifications_to_users, sender=Notification)
