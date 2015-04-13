import json

from core.drf.mixins import NestedGenericModelMixin

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from cla_eventlog import event_registry

from legalaid.models import Case

from diagnosis.models import DiagnosisTraversal
from diagnosis.serializers import DiagnosisSerializer


class BaseDiagnosisViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet
):

    serializer_class = DiagnosisSerializer
    PARENT_FIELD = 'diagnosis'
    model = DiagnosisTraversal
    lookup_field = 'reference'

    @action()
    def move_down(self, request, **kwargs):
        return self.partial_update(request, **kwargs)

    @action()
    def move_up(self, request, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(self.object)

        self.object = serializer.move_up()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_diagnosis_log(self, obj, status):
        try:
            obj.case
        except Case.DoesNotExist:
            return

        diagnosis_event = event_registry.get_event('diagnosis')()
        patch = json.dumps(self.get_serializer_class()(obj).data)

        kwargs = {
            'created_by': self.get_current_user(),
            'status': status,
            'patch': patch
        }
        diagnosis_event.process(obj.case, **kwargs)

    def post_delete(self, obj, *args, **kwargs):
        ret = super(BaseDiagnosisViewSet, self).post_delete(obj, *args, **kwargs)
        if obj.is_state_unknown():
            self.create_diagnosis_log(obj, status='incomplete_deleted')
        else:
            self.create_diagnosis_log(obj, status='deleted')
        return ret

    def pre_save(self, obj, *args, **kwargs):
        self._original_obj = self.get_object()
        return super(BaseDiagnosisViewSet, self).pre_save(obj, *args, **kwargs)

    def post_save(self, obj, *args, **kwargs):
        ret = super(BaseDiagnosisViewSet, self).post_save(obj, *args, **kwargs)
        if not obj.is_state_unknown():
            if not self._original_obj or self._original_obj.is_state_unknown():
                self.create_diagnosis_log(obj, status='created')
        return ret

    def get_current_user(self):
        return self.request.user
