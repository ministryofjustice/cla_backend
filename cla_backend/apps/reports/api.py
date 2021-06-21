# coding=utf-8
from rest_framework.authentication import SessionAuthentication
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from core.models import get_web_user

from .serializers import ExportSerializer
from .models import Export


class ExportListView(generics.ListAPIView, generics.DestroyAPIView):
    serializer_class = ExportSerializer
    model = Export
    permission_classes = (IsAdminUser,)
    authentication_classes = (SessionAuthentication,)
    page_size = 1000
    scheduled = False

    def get_queryset(self):
        if self.scheduled:
            user = get_web_user()
        else:
            user = self.request.user

        return super(ExportListView, self).get_queryset().filter(user=user)
