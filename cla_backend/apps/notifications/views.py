# coding=utf-8
from rest_framework import mixins, viewsets

from .models import Notification
from .serializers import NotificationSerializer


class BaseNotificationViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def get_queryset(self):
        return Notification.objects.live()
