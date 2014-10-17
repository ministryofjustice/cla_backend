from rest_framework import serializers

from core.serializers import ClaModelSerializer

from .models import Timer


class TimerSerializer(ClaModelSerializer):

    class Meta:
        model = Timer
        fields = ('created',)
