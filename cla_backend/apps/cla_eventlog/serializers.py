from rest_framework import serializers

from core.serializers import JSONField, ClaModelSerializer

from cla_eventlog.models import Log


class LogSerializerBase(ClaModelSerializer):
    code = serializers.CharField(read_only=True)
    created_by = serializers.CharField(read_only=True, source="created_by.username")
    created = serializers.DateTimeField(read_only=True)
    level = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    timer_id = serializers.IntegerField(read_only=True)
    notes = serializers.CharField(read_only=True)
    patch = JSONField(read_only=True)

    class Meta(object):
        model = Log
        fields = ()
