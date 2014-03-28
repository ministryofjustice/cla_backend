from call_centre.serializers import EligibilityCheckSerializer, CategorySerializer, \
    CaseSerializer
from legalaid.models import Category, EligibilityCheck, Case
from rest_framework import viewsets, mixins

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

    lookup_field = 'code'


class EligibilityCheckViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = EligibilityCheck
    serializer_class = EligibilityCheckSerializer

    lookup_field = 'reference'


class CaseViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Case.objects.all().order_by('-modified')
    model = Case
    lookup_field = 'reference'
    serializer_class = CaseSerializer