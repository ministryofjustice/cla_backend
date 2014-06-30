from cla_eventlog.models import Log
from core.serializers import ClaModelSerializer
from rest_framework import serializers


class LogSerializerBase(ClaModelSerializer):

    code = serializers.CharField(read_only=True)
    created_by = serializers.CharField(read_only=True, source='created_by.username')
    created = serializers.DateTimeField(read_only=True)
    level = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    notes = serializers.CharField(read_only=True)

    class Meta:
        model = Log
        fields = None