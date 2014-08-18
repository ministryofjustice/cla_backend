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

        user = self.request.user

        diagnosis_event = event_registry.get_event('diagnosis')()
        patch = json.dumps(self.get_serializer_class()(obj).data)

        kwargs = {
            'created_by': user,
            'status': status,
            'patch': patch
        }
        diagnosis_event.process(obj.case, **kwargs)

    def post_delete(self, obj, *args, **kwargs):
        ret = super(BaseDiagnosisViewSet, self).post_delete(obj, *args, **kwargs)
        self.create_diagnosis_log(obj, status='deleted')
        return ret

    def pre_save(self, obj, *args, **kwargs):
        original_obj = self.get_object()
        self._original_state = original_obj.state if original_obj else None
        return super(BaseDiagnosisViewSet, self).pre_save(obj, *args, **kwargs)

    def post_save(self, obj, *args, **kwargs):
        ret = super(BaseDiagnosisViewSet, self).post_save(obj, *args, **kwargs)
        if not self._original_state and obj.state:
            self.create_diagnosis_log(obj, status='created')
        return ret
