from rest_framework import serializers

from core.serializers import ClaModelSerializer

from .models import Timer


class TimerSerializer(ClaModelSerializer):
    created_by = serializers.CharField(read_only=True,
                                       source='created_by.username')

    class Meta:
        model = Timer
        fields = ('created', 'created_by')
