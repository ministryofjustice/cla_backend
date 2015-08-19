# -*- coding: utf-8 -*-
from cla_eventlog import event_registry
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response as DRFResponse
from complaints.forms import BaseComplaintLogForm
from core.drf.mixins import FormActionMixin
from django.contrib.auth.models import AnonymousUser

from .models import Complaint, Category
from rest_framework.decorators import action
from .serializers import ComplaintSerializerBase, CategorySerializerBase


class ComplaintFormActionMixin(FormActionMixin):
    """
    This is for backward compatibility
    """
    FORM_ACTION_OBJ_PARAM = 'complaint'


class BaseComplaintViewSet(
    ComplaintFormActionMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = Complaint
    serializer_class = ComplaintSerializerBase

    def pre_save(self, obj, *args, **kwargs):
        super(BaseComplaintViewSet, self).pre_save(obj)

        user = self.request.user
        if not obj.pk and not isinstance(user, AnonymousUser):
            obj.created_by = user

    def post_save(self, obj, created=False):
        if created:
            dt = timezone.now()
            notes = u"Complaint created on {dt} by {user}. {notes}".format(
                dt=dt.strftime("%d/%m/%Y %H:%M"),
                user=self.request.user.username,
                notes=obj.description
            )

            event = event_registry.get_event('complaint')()
            event.process(
                obj.eod.case,
                created_by=self.request.user,
                notes=notes,
                complaint=obj,
                code='COMPLAINT_CREATED'
            )

    @action()
    def add_event(self, request, **kwargs):
        obj = self.get_object()
        form = BaseComplaintLogForm(complaint=obj, data=request.DATA)
        if form.is_valid():
            form.save(request.user)
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )


class BaseComplaintCategoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = Category
    serializer_class = CategorySerializerBase
