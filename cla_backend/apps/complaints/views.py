# -*- coding: utf-8 -*-
import textwrap
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.text import capfirst, force_text
from rest_framework import viewsets, mixins, status, views as rest_views
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse

from cla_eventlog import event_registry
from cla_eventlog.models import ComplaintLog
from complaints.forms import ComplaintLogForm
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

    def get_queryset(self, dashboard=False, show_closed=False):
        qs = super(BaseComplaintViewSet, self).get_queryset()

        sql_params = {
            # NB: ensure these are always sql-safe
            'complaint_ct': ContentType.objects.get_for_model(Complaint).id,
            'closed_code': 'COMPLAINT_CLOSED',
        }
        qs = qs.extra(
            select={
                'closed': '''
                    SELECT cla_eventlog_log.created FROM cla_eventlog_log
                    WHERE
                        cla_eventlog_log.content_type_id={complaint_ct}
                        AND cla_eventlog_log.object_id=complaints_complaint.id
                        AND cla_eventlog_log.code='{closed_code}'
                    ORDER BY cla_eventlog_log.created DESC
                    LIMIT 1
                    '''.format(**sql_params)
            }
        )
        if dashboard and not show_closed:
            qs = qs.extra(
                where=[
                    '''
                    SELECT COUNT(id) < 1 FROM cla_eventlog_log
                    WHERE
                        cla_eventlog_log.content_type_id={complaint_ct}
                        AND cla_eventlog_log.object_id=complaints_complaint.id
                        AND cla_eventlog_log.code='{closed_code}'
                    '''.format(**sql_params)
                ]
            )
        return qs

    def pre_save(self, obj, *args, **kwargs):
        super(BaseComplaintViewSet, self).pre_save(obj)

        user = self.request.user
        if not obj.pk:
            if not isinstance(user, AnonymousUser):
                obj.created_by = user
            obj.update_owner = bool(obj.owner)
        else:
            original_obj = self.model.objects.get(pk=obj.pk)
            obj.update_owner = original_obj.owner_id != obj.owner_id

    def post_save(self, obj, created=False):
        if created:
            dt = timezone.now()
            description = u'%s\n\nOriginal expressions of dissatisfaction:\n%s\n\n%s' % (
                obj.description or u'',
                u'\n'.join(map(lambda desc: u'- %s' % desc,
                               obj.eod.category_descriptions)),
                obj.eod.notes,
            )
            notes = u'Complaint created on {dt} by {user}.\n\n{description}'.format(
                dt=dt.strftime("%d/%m/%Y %H:%M"),
                user=self.request.user.username,
                description=description.strip(),
            ).strip()

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
        form = ComplaintLogForm(complaint=obj, data=request.DATA)
        if form.is_valid():
            form.save(request.user)
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )

    @action()
    def reopen(self, request, pk):
        obj = self.get_object()
        closed_logs = obj.logs.filter(code='COMPLAINT_CLOSED')
        if not closed_logs.exists():
            return DRFResponse('Cannot reopen a complaint that is not closed',
                               status=status.HTTP_400_BAD_REQUEST)

        dt = timezone.now()
        last_closed = closed_logs.order_by('-created').first()
        notes = u'''
            Complaint reopened on {dt_reopen} by {user_reopen}.
            Originally closed {dt_closed} by {user_closed}.
        '''.format(
            dt_reopen=dt.strftime("%d/%m/%Y %H:%M"),
            user_reopen=request.user.username,
            dt_closed=last_closed.created.strftime("%d/%m/%Y %H:%M"),
            user_closed=last_closed.created_by.username,
        )
        notes = textwrap.dedent(notes).strip()
        notes += u'\n\n' + last_closed.notes

        event = event_registry.get_event('complaint')()
        event.process(
            obj.eod.case,
            created_by=request.user,
            notes=notes.strip(),
            complaint=obj,
            code='COMPLAINT_REOPENED',
        )

        closed_logs.delete()
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)


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

    @classmethod
    def make_bool_choices(cls, *args):
        return [
            dict(zip(('value', 'description'), item))
            for item
            in zip((True, False), args)
        ]

    def get(self, *args, **kwargs):
        return DRFResponse({
            'justified': self.make_bool_choices('Justified', 'Unjustified'),
            'resolved': self.make_bool_choices('Resolved', 'Unresolved'),
            'levels': self.get_field_choices('level'),
            'sources': self.get_field_choices('source'),
            'actions': [
                {
                    'value': event_code,
                    'description': event_details['description'],
                }
                for event_code, event_details
                in ComplaintLogForm.get_operator_code_objects()
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
