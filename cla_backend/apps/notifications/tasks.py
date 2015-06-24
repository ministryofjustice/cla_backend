# -*- coding: utf-8 -*-
import json
import requests
from celery import shared_task
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from .models import Notification
from .serializers import NotificationSerializer


@shared_task(default_retry_delay=1, max_retries=12)
def send_notifications():
    data = {
        'notifications': NotificationSerializer(
            Notification.objects.live(),
            many=True).data
    }

    response = requests.post(
        '%s:%s/admin/notifications/' % (settings.FRONTEND_HOST_NAME,
                                        settings.EXPRESS_SERVER_PORT),
        data=json.dumps(data, cls=DjangoJSONEncoder),
        headers={'content-type': 'application/json'}
    )
    try:
        success = response.json()['success']
        assert success is True
    except (ValueError, AssertionError) as e:
        raise send_notifications.retry(exc=e)
    else:
        return success

