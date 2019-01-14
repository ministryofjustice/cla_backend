from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings
from raven.contrib.celery import register_logger_signal, register_signal

# set the default Django settings module for the 'celery' program.
from raven.scripts.runner import send_test_message

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cla_backend.settings")
app = Celery("cla_backend")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

client = None
if hasattr(settings, "RAVEN_CONFIG"):
    from raven.contrib.django.models import client

    register_logger_signal(client)
    register_signal(client)


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


@app.task()
def sentry_test_task():
    if client:
        send_test_message(client, {})
