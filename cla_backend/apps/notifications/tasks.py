# coding=utf-8
import json
import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from .models import Notification
from .serializers import NotificationSerializer

logger = get_task_logger(__name__)


@shared_task(default_retry_delay=1, max_retries=12)
def send_notifications():
    data = {"notifications": NotificationSerializer(Notification.objects.live(), many=True).data}
    url = "%s:%s/admin/notifications/" % (settings.EXPRESS_SERVER_HOST, settings.EXPRESS_SERVER_PORT)
    data = json.dumps(data, cls=DjangoJSONEncoder)
    logger.info("Sending notification - url %s" % url)
    logger.info("Sending notification - data %s" % data)
    response = requests.post(url, data=data, headers={"content-type": "application/json"})

    try:
        success = response.json()["success"]
        assert success is True
    except (ValueError, AssertionError) as e:
        raise send_notifications.retry(exc=e)
    else:
        return success
