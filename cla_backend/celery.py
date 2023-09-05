from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
# from cla_backend.apps.notifications.tasks import send_notifications
# from cla_backend.apps.notifications.models import Notification
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cla_backend.settings")
app = Celery("cla_backend")




# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     def create_crontab_from_datetime(dt):
#         return crontab(
#             hour=dt.hour,
#             minute=dt.minute,
#             day_of_month=dt.day,
#             month_of_year=dt.month,
#         )
#
#     # Schedule upcoming notifications
#     for notification in Notification.objects.upcoming():
#         schedule = create_crontab_from_datetime(notification.start_time)
#         sender.add_periodic_task(schedule, send_notifications.s())


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):

    print "This is a test"

@app.task()
def another_task():
    print "I am inside another_task"
