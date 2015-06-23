# -*- coding: utf-8 -*-
import datetime
from django.core.cache import cache
import pytz


def get_update_client_times(instance):
    from .tasks import CACHE_KEY
    times = []
    cached_notifications = cache.get(CACHE_KEY, [])
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    try:
        cached_instance_data = next(n for (i, n) in
                                    enumerate(cached_notifications)
                                    if n["id"] == instance.pk)
        if cached_instance_data['start_time'] < now < instance.start_time:
            times.append({})
    except StopIteration:
        pass

    task_id = '%s-%s' % (CACHE_KEY, instance.pk)
    times.append({'eta': instance.start_time, 'task_id': '%s-start' % task_id})
    times.append({'eta': instance.end_time, 'task_id': '%s-end' % task_id})

    return times


def send_notifications_to_users(sender, instance, **kwargs):
    from .tasks import send_notifications

    for kwargs in get_update_client_times(instance):
        send_notifications.apply_async(**kwargs)




