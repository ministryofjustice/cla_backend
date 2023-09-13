# coding=utf-8
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from model_utils.models import TimeStampedModel

from .constants import NOTIFICATION_TYPES
from .signals import schedule_notifications_to_users, un_schedule_notifications_to_users

MAX_NOTIFICATION_RETRIES = 3


class NotificationManager(models.Manager):
    def live(self):
        now = timezone.now()
        return self.get_queryset().filter(start_time__lt=now, end_time__gt=now)


class ScheduleManager(models.Manager):
    def live(self):
        now = timezone.now()
        return self.get_queryset().filter(
            notification__start_time__lt=now,
            notification__end_time__gt=now,
            completed=False, retried__lt=MAX_NOTIFICATION_RETRIES
        )


class Notification(TimeStampedModel):
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="notification")
    notification = models.CharField(max_length=100)
    description = models.CharField(max_length=600, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = NotificationManager()


class Schedule(TimeStampedModel):
    notification = models.ForeignKey(Notification)
    retried = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="scheduled")
    completed = models.BooleanField(default=False)
    objects = ScheduleManager()


post_save.connect(schedule_notifications_to_users, sender=Notification)
post_delete.connect(un_schedule_notifications_to_users, sender=Notification)
