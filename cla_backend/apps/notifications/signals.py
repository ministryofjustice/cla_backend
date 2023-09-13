# coding=utf-8
from django.utils import timezone


def schedule_notifications_to_users(sender, instance, **kwargs):
    from notifications.models import Schedule
    now = timezone.now()

    defaults = {}
    # Reset schedule when updating notification to start in the future
    if instance.start_time > now:
        defaults["retried"] = 0
        defaults["completed"] = False
        defaults["status"] = "scheduled"
    Schedule.objects.update_or_create(notification=instance, defaults=defaults)


def un_schedule_notifications_to_users(sender, instance, **kwargs):
    from notifications.models import Schedule
    Schedule.objects.filter(notification=instance).delete()
