# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import json
import pytz
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


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
            '.'.join([self.time_string, self.period, self.variable])
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
    def time_string(self):
        return self.timestamp.replace(tzinfo=pytz.utc).isoformat()

    @property
    def url(self):
        return '%s%s' % (settings.PERFORMANCE_PLATFORM_API, self.endpoint)

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
    """
    endpoint = 'application-stage-volumes'

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

    def _count(self):
        return 1000


class TransactionsByChannelTypeSerializer(PPSerializer):
    """
    Schema:
    {
        "_id": "url-friendly Base64 encoding of '<_timestamp>.<period>.<channel_type>.<channel>'",
        "_timestamp": "2015-06-10T00:00:00+00:00",
        "period": "week",
        "channel_type": "digital",
        "channel": "phone",
        "count": 2000
    }
    """
    variable_key = 'channel'
    endpoint = 'transactions-by-channel-type'

    @property
    def id(self):
        return base64.b64encode(
            '.'.join([
                self.time_string,
                self.period,
                self.channel_type,
                self.channel
            ])
        )

    def _count(self):
        return 2000
