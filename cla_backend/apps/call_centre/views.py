from call_centre.serializers import EligibilityCheckSerializer, CategorySerializer, \
    CaseSerializer, ProviderSerializer
from cla_provider.models import Provider
from django import http
from django.shortcuts import redirect
from legalaid.models import Category, EligibilityCheck, Case
from rest_framework import viewsets, mixins
from rest_framework.decorators import action


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

    def pre_save(self, obj):
        if not obj.pk:
            obj.created_by = self.request.user

    @action()
    def close(self, request, pk=None, **kwargs):
        obj = self.get_object()
        return http.HttpResponse(status=204)


class ProviderViewSet(viewsets.ReadOnlyModelViewSet):
    model = Provider
    serializer_class = ProviderSerializer

