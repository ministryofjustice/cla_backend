import json
from call_centre.forms import ProviderAllocationForm
from call_centre.serializers import EligibilityCheckSerializer, CategorySerializer, \
    CaseSerializer, ProviderSerializer
from cla_common.constants import CASE_STATE_CLOSED, CASE_STATE_OPEN
from cla_provider.models import Provider
from django import http
from django.contrib.auth.models import AnonymousUser
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
    queryset = Case.objects.filter(state=CASE_STATE_OPEN, provider=None).order_by('-modified')
    model = Case
    lookup_field = 'reference'
    serializer_class = CaseSerializer

    def pre_save(self, obj):
        user = self.request.user
        if not obj.pk and not isinstance(user, AnonymousUser):
            obj.created_by = user

    # TODO: this is not needed yet - front end can handle \
    # this logic for now.

    # @action()
    # def assign(self, request, reference=None, **kwargs):
    #     obj = self.get_object()
    #     form = ProviderAllocationForm(request.POST)
    #     if form.is_valid():
    #         data = form.cleaned_data
    #         obj.provider_id = data['provider']
    #         return http.HttpResponse(status=204)
    #     return http.HttpResponseBadRequest(content=json.dumps(form.errors))
    #
    # @action()
    # def assign(self, request, reference=None, **kwargs):
    #     obj = self.get_object()
    #     form = ProviderAllocationForm(request.POST)
    #     if form.is_valid():
    #         data = form.cleaned_data
    #         obj.provider_id = data['provider']
    #         return http.HttpResponse(status=204)
    #     return http.HttpResponseBadRequest(content=json.dumps(form.errors))


class ProviderViewSet(viewsets.ReadOnlyModelViewSet):
    model = Provider
    serializer_class = ProviderSerializer

