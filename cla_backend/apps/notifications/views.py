# coding=utf-8
from rest_framework import mixins

from core.drf.viewsets import CompatGenericViewSet

from .models import Notification
from .serializers import NotificationSerializer


class BaseNotificationViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, CompatGenericViewSet):
    serializer_class = NotificationSerializer
    model = Notification

    def get_queryset(self):
        return Notification.objects.live()
