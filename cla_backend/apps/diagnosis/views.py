import json

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from core.drf.mixins import NestedGenericModelMixin, ClaCreateModelMixin, ClaUpdateModelMixin
from cla_eventlog import event_registry
from legalaid.models import Case
from diagnosis.models import DiagnosisTraversal
from diagnosis.serializers import DiagnosisSerializer


class DiagnosisModelMixin(object):
    serializer_class = DiagnosisSerializer
    model = DiagnosisTraversal
    queryset = DiagnosisTraversal.objects.all()
    lookup_field = "reference"

    @detail_route(methods=["post"])
    def move_down(self, request, **kwargs):
        return self.partial_update(request, **kwargs)

    @detail_route(methods=["post"])
    def move_up(self, request, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data={})

        serializer.move_up()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_diagnosis_log(self, obj, status):
        try:
            obj.case
        except Case.DoesNotExist:
            return

        diagnosis_event = event_registry.get_event("diagnosis")()
        patch = json.dumps(self.get_serializer_class()(obj).data)

        kwargs = {"created_by": self.get_current_user(), "status": status, "patch": patch}
        diagnosis_event.process(obj.case, **kwargs)

    def perform_destroy(self, instance):
        super(DiagnosisModelMixin, self).perform_destroy(instance)
        if instance.is_state_unknown():
            self.create_diagnosis_log(instance, status="incomplete_deleted")
        else:
            self.create_diagnosis_log(instance, status="deleted")

    def perform_create(self, serializer):
        self._original_obj = self.get_object()
        return super(DiagnosisModelMixin, self).perform_create(serializer)

    def perform_update(self, serializer):
        self._original_obj = self.get_object()
        super(DiagnosisModelMixin, self).perform_update(serializer)

    def post_save(self, obj, *args, **kwargs):
        ret = super(DiagnosisModelMixin, self).post_save(obj, *args, **kwargs)
        if not obj.is_state_unknown():
            if not self._original_obj or self._original_obj.is_state_unknown():
                self.create_diagnosis_log(obj, status="created")
        return ret

    def get_current_user(self):
        return self.request.user


class BaseDiagnosisViewSet(
    DiagnosisModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet,
    ClaCreateModelMixin,
    ClaUpdateModelMixin,
):
    PARENT_FIELD = "diagnosis"
