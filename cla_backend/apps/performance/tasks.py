# coding=utf-8
from __future__ import unicode_literals
import datetime
from cla_common.constants import CASE_SOURCE
import requests
from celery import shared_task
from celery import Task
import logging

from performance.constants import PERFORMANCE_STAGES, PERFORMANCE_STATES, PERFORMANCE_CHANNELS
from .serializers import (
    ApplicationStageVolumeSerializer,
    ApplicationStateVolumeSerializer,
    TransactionsByChannelTypeSerializer,
)

logger = logging.getLogger(__name__)


@shared_task(default_retry_delay=10, max_retries=12, bind=True)
def post_task(self, url, data, headers):
    response = requests.post(url, data=data, headers=headers)

    try:
        response_json = response.json()
    except ValueError:
        response_json = None

    if response.status_code != 200 and response_json is not None and response_json.get("status") != "ok":
        logger.error(
            "Performance post failure to %s" % url,
            extra={"data": data, "headers": headers, "response_text": response.text},
        )
        self.retry(args=[url, data, headers])


class BasePerformanceTask(Task):
    variables = {}
    serializer_class = None

    def task_kwargs_list(self):
        kwl = []
        for key, variables in self.variables.items():
            other_vars = filter(lambda item: item[0] is not key, self.variables.items())
            for variable in variables:
                if other_vars:
                    for k, vs in other_vars:
                        for v in vs:
                            kw = {key: variable, k: v}
                            if kw not in kwl:
                                kwl.append(kw)
                else:
                    kwl.append({key: variable})

        return kwl

    def run(self, *args, **kwargs):
        for task_kwargs in self.task_kwargs_list():
            serializer = self.serializer_class(datetime.datetime.now(), **task_kwargs)
            post_task.delay(url=serializer.url, data=serializer.json, headers=serializer.headers)


class ApplicationStageVolumeTask(BasePerformanceTask):
    variables = {"stage": PERFORMANCE_STAGES}
    serializer_class = ApplicationStageVolumeSerializer


class ApplicationStateVolumeTask(BasePerformanceTask):
    variables = {"state": PERFORMANCE_STATES}
    serializer_class = ApplicationStateVolumeSerializer


class TransactionsByChannelTypeTask(BasePerformanceTask):
    variables = {"channel_type": PERFORMANCE_CHANNELS, "channel": [c[0] for c in CASE_SOURCE]}
    serializer_class = TransactionsByChannelTypeSerializer


@shared_task(default_retry_delay=10, max_retries=12)
def send_all_performance_data():
    # ApplicationStageVolumeTask().delay()
    # ApplicationStateVolumeTask().delay()
    TransactionsByChannelTypeTask().delay()
