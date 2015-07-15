# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import json
import datetime
from cla_common.constants import ELIGIBILITY_STATES, DIAGNOSIS_SCOPE
import pytz
import logging
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from diagnosis.models import DiagnosisTraversal
from django.db.models import Q
from legalaid.models import Case, EligibilityCheck

logger = logging.getLogger(__name__)


class PPSerializer(object):
    endpoint = None
    variables = {}

    def __init__(self, timestamp, period='week', **data_types):
        self.timestamp = timestamp
        self.data_types = data_types
        self.period = period
        self.__dict__.update(data_types)
        super(PPSerializer, self).__init__()

    @property
    def id(self):
        return base64.b64encode(
            '.'.join([self.time_string, self.period, self._variable])
        )

    @property
    def headers(self):
        return {
            'content-type': 'application/json',
            'Authorization': 'Bearer %s' % settings.PERFORMANCE_PLATFORM_TOKEN
        }

    @property
    def count(self):
        return self._count()

    @property
    def from_time(self):
        day_start = self.timestamp.replace(hour=0, minute=0, second=0,
                                           microsecond=0)
        return day_start - datetime.timedelta(days=day_start.weekday()) - \
            datetime.timedelta(weeks=1)

    @property
    def to_time(self):
        return self.from_time + datetime.timedelta(weeks=1)

    @property
    def time_string(self):
        return self.from_time.replace(tzinfo=pytz.utc).isoformat()

    @property
    def url(self):
        return '%s%s' % (settings.PERFORMANCE_PLATFORM_API, self.endpoint)

    @property
    def _variable(self):
        raise NotImplementedError

    def _count(self):
        raise NotImplementedError

    def _data(self):
        data = {
            "_id": self.id,
            "_timestamp": self.time_string,
            "period": self.period,
            "count": self.count,
        }
        data.update(self.data_types)
        return data

    @property
    def data(self):
        return self._data()

    @property
    def json(self):
        return json.dumps(self.data, cls=DjangoJSONEncoder)


class ApplicationStageVolumeSerializer(PPSerializer):
    """
    Schema:
    return {
        "_id": "url-friendly Base64 encoding of '<_timestamp>.<period>.<stage>'",
        "_timestamp": "2015-06-10T00:00:00+00:00",
        "period": "week",
        "stage": "created",
        "count": 100
    }

    - checked (by call-centre agents irrespective of channel)
    - verified (met criteria set down by agents following call-back)
    - referred (notification sent to specialist solicitor)
    - accepted (case checked and accepted by specialist
    - closed (case complete)
    """
    endpoint = 'application-stage-volumes'

    @property
    def _variable(self):
        return self.stage

    def _count(self):
        return 100


class ApplicationStateVolumeSerializer(PPSerializer):
    """
    Schema:
    {
        "_id": "url-friendly Base64 encoding of '<_timestamp>.<period>.<state>'",
        "_timestamp": "2015-06-10T00:00:00+00:00",
        "period": "week",
        "state": "started",
        "count": 1000
    }
    """
    endpoint = 'application-state-volumes'

    @property
    def _variable(self):
        return self.state

    def _count(self):
        return 1000


class TransactionsByChannelTypeSerializer(PPSerializer):
    """
    Schema:
    {
        "_id": "url-friendly Base64 encoding of '<_timestamp>.<period>.<channel_type>.<channel>'",
        "_timestamp": "2015-06-10T00:00:00+00:00",
        "period": "week",
        "channel_type": 'digital', 'non-digital', 'assisted-digital',
        "channel": 'PHONE', 'VOICEMAIL', 'SMS', 'WEB'
        "count": 2000
    }
    """
    endpoint = 'transactions-by-channel-type'

    @property
    def _variable(self):
        return '.'.join([self.channel_type, self.channel])

    def _get_cases(self):
        return Case.objects.filter(
            source=self.channel,
            created__gte=self.from_time,
            created__lte=self.to_time
        )

    def _get_eligibility_checks(self):
        return EligibilityCheck.objects.filter(
            created__gte=self.from_time,
            created__lte=self.to_time
        )

    def _get_diagnosis_traversals(self):
        return DiagnosisTraversal.objects.filter(
            created__gte=self.from_time,
            created__lte=self.to_time
        )

    def _non_digital(self):
        if self.channel == 'WEB':
            return 0
        return self._get_cases().count()

    def _digital(self):
        if self.channel != 'WEB':
            return 0
        cases = self._get_cases().filter(
            ~Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN) |
            Q(Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN) &
              Q(eligibility_check__property_set__share__isnull=True))
        )
        ecs = self._get_eligibility_checks().filter(
            ~Q(state=ELIGIBILITY_STATES.UNKNOWN) & Q(case__isnull=True)
        )
        diags = self._get_diagnosis_traversals().filter(
            Q(case__isnull=True) & ~Q(state=DIAGNOSIS_SCOPE.UNKNOWN)
        )
        return cases.count() + ecs.count() + diags.count()

    def _assisted_digital(self):
        if self.channel != 'WEB':
            return 0
        cases = self._get_cases().filter(
            Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN) |
            Q(eligibility_check__isnull=True) &
            ~Q(Q(eligibility_check__state=ELIGIBILITY_STATES.UNKNOWN) &
               Q(eligibility_check__property_set__share__isnull=True))
        )
        return cases.count()

    def _count(self):
        val = getattr(self, '_%s' % self.channel_type.replace('-', '_'))()

        logger.info('Successful performance calc: %s, %s: %s' %
                    (self.channel_type, self.channel, val))

        return val


