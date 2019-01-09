# -*- coding: utf-8 -*-
from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Notification
        fields = ("id", "type", "notification", "description", "start_time", "end_time")
