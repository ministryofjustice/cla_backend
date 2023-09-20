import json
import requests
from celery import current_app
from celery.utils.log import get_logger
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from .models import Schedule, MAX_NOTIFICATION_RETRIES
from .serializers import NotificationSerializer

logger = get_logger("celery.beat")


def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(180, push_notifications.s(), name='Push notifications every 3 minutes')


@current_app.task
def push_notifications():
    logger.info("Notifications: Running push notifications")
    schedules = Schedule.objects.live()
    if not schedules:
        logger.info("Notifications: No schedules found")
        return

    notifications = []
    for schedule in schedules:
        if schedule.notification not in notifications:
            notifications.append(schedule.notification)

    try:
        success = _send_notifications(notifications)
    except (ValueError, AssertionError, requests.exceptions.RequestException):
        logger.info("Notifications: Failed sending notifications")
        for schedule in schedules:
            schedule.retried += 1
            schedule.status = "failed"
            schedule.completed = schedule.retried >= MAX_NOTIFICATION_RETRIES
            schedule.save()
    else:
        logger.info("Notifications: notifications successfully sent")
        schedules.update(status="success", completed=True)
        return success


def _send_notifications(notifications):
    url = "%s:%s/admin/notifications/" % (settings.EXPRESS_SERVER_HOST, settings.EXPRESS_SERVER_PORT)
    data = {"notifications": NotificationSerializer(notifications, many=True).data}
    data = json.dumps(data, cls=DjangoJSONEncoder)
    logger.info("Notifications: url %s" % url)
    logger.info("Notifications: data %s" % data)
    response = requests.post(
        url,
        data=data,
        headers={"content-type": "application/json"},
    )
    success = response.json()["success"]
    assert success is True
    return success
