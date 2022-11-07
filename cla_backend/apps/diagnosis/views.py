import json

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from core.drf.mixins import NestedGenericModelMixin, ClaCreateModelMixin, ClaUpdateModelMixin
from cla_eventlog import event_registry
from legalaid.models import Case
from diagnosis.models import DiagnosisTraversal
from diagnosis.serializers import DiagnosisSerializer

from cla_common.constants import DIAGNOSIS_SCOPE


class DiagnosisModelMixin(object):
    serializer_class = DiagnosisSerializer
    queryset = DiagnosisTraversal.objects.all()
    lookup_field = "reference"

    @detail_route(methods=["post"])
    def move_down(self, request, **kwargs):
        return self.partial_update(request, **kwargs)

    @detail_route(methods=["post"])
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

        diagnosis_event = event_registry.get_event("diagnosis")()
        patch = json.dumps(self.get_serializer_class()(obj).data)

        kwargs = {"created_by": self.get_current_user(), "status": status, "patch": patch}
        diagnosis_event.process(obj.case, **kwargs)

    def post_delete(self, obj, *args, **kwargs):
        ret = super(DiagnosisModelMixin, self).post_delete(obj, *args, **kwargs)
        if obj.is_state_unknown():
            self.create_diagnosis_log(obj, status="incomplete_deleted")
        else:
            self.create_diagnosis_log(obj, status="deleted")
        return ret

    def perform_create(self, serializer):
        previous_state = serializer.validated_data.get("state", DIAGNOSIS_SCOPE.UNKNOWN)
        obj = super(DiagnosisModelMixin, self).perform_create(serializer)
        self._post_save(obj, previous_state)
        return obj

    def perform_update(self, serializer):
        previous_state = serializer.instance.state
        super(DiagnosisModelMixin, self).perform_update(serializer)
        self._post_save(serializer.instance, previous_state)

    def _post_save(self, obj, previous_state):
        if not obj.is_state_unknown() and DiagnosisTraversal.is_state_unknown_cls(previous_state):
            self.create_diagnosis_log(obj, status="created")

    def get_current_user(self):
        return self.request.user


class BaseDiagnosisViewSet(
    DiagnosisModelMixin,
    ClaCreateModelMixin,
    mixins.RetrieveModelMixin,
    ClaUpdateModelMixin,
    mixins.DestroyModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet,
):
    PARENT_FIELD = "diagnosis"
