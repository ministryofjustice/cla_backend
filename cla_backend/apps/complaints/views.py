# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.text import capfirst, force_text
from rest_framework import viewsets, mixins, status, views as rest_views
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_LEVELS
from cla_eventlog.models import ComplaintLog
from complaints.forms import BaseComplaintLogForm
from core.drf.mixins import FormActionMixin, NestedGenericModelMixin

from .models import Complaint, Category
from .serializers import ComplaintSerializerBase, CategorySerializerBase, \
    ComplaintLogSerializerBase


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
        if not obj.pk:
            if not isinstance(user, AnonymousUser):
                obj.created_by = user
            obj.update_owner = True
        else:
            original_obj = self.model.objects.get(pk=obj.pk)
            obj.update_owner = original_obj.owner_id != obj.owner_id

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

        if getattr(obj, 'update_owner', False):
            event = event_registry.get_event('complaint')()
            event.process(
                obj.eod.case,
                created_by=self.request.user,
                notes=u'Owner set to %s' % (obj.owner.get_full_name() or obj.owner.username),
                complaint=obj,
                code='OWNER_SET'
            )

    @action()
    def add_event(self, request, pk):
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


class BaseComplaintConstantsView(rest_views.APIView):
    @classmethod
    def get_field_choices(cls, key):
        return [
            {
                'value': choice[0],
                'description': capfirst(force_text(choice[1]).lower()),
            }
            for choice in Complaint._meta.get_field(key).choices
        ]

    def get(self, *args, **kwargs):
        return DRFResponse({
            'levels': [
                {
                    'value': LOG_LEVELS.HIGH,
                    'description': 'Major',
                },
                {
                    'value': LOG_LEVELS.MINOR,
                    'description': 'Minor',
                },
            ],
            'sources': self.get_field_choices('source'),
            'justified': [
                {
                    'value': True,
                    'description': 'Justified',
                },
                {
                    'value': False,
                    'description': 'Unjustified',
                },
            ],
        })


class BaseComplaintLogViewset(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet
):
    model = ComplaintLog
    serializer_class = ComplaintLogSerializerBase
    lookup_field = 'pk'
    PARENT_FIELD = 'logs'

    def get_queryset(self):
        content_type = ContentType.objects.get_for_model(
            Complaint)
        return self.model.objects.filter(
            object_id=self.kwargs.get('complaint_pk'),
            content_type=content_type)
