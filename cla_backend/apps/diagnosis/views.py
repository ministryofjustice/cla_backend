from core.drf.mixins import NestedGenericModelMixin

from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

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
