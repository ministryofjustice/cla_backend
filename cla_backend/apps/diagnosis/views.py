from core.drf.mixins import NestedGenericModelMixin
from diagnosis.models import DiagnosisTraversal
from diagnosis.serializers import DiagnosisSerializer

from rest_framework import mixins, viewsets


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
