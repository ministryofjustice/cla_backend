# -*- coding: utf-8 -*-
from django.utils import timezone

TASK_ID_PREFIX = "cla_backend.notifications.task.notifications"


def get_update_client_times(instance):
    times = []
    now = timezone.now()
    task_id = "%s-%s" % (TASK_ID_PREFIX, instance.pk)

    times.append({})
    if instance.start_time > now:
        times.append({"eta": instance.start_time, "task_id": "%s-start" % task_id})
    times.append({"eta": instance.end_time, "task_id": "%s-end" % task_id})

    return times


def send_notifications_to_users(sender, instance, **kwargs):
    from .tasks import send_notifications

    for kwargs in get_update_client_times(instance):
        send_notifications.apply_async(**kwargs)
