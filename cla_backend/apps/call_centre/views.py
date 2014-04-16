import json

from django.contrib.auth.models import AnonymousUser

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import OrderingFilter, SearchFilter

from django import http

from cla_common.constants import CASE_STATE_OPEN, \
    CASE_STATE_CHOICES
from cla_provider.models import Provider
from legalaid.models import Category, EligibilityCheck, Case, OutcomeCode
from core.viewsets import IsEligibleActionViewSetMixin

from .permissions import CallCentreClientIDPermission
from .serializers import EligibilityCheckSerializer, CategorySerializer, \
    CaseSerializer, ProviderSerializer, OutcomeCodeSerializer
from .forms import ProviderAllocationForm


class CallCentrePermissionsViewSetMixin(object):
    permission_classes = (CallCentreClientIDPermission,)


class CategoryViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

    lookup_field = 'code'


class OutcomeCodeViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = OutcomeCode
    serializer_class = OutcomeCodeSerializer

    lookup_field = 'code'


class EligibilityCheckViewSet(
    CallCentrePermissionsViewSetMixin,
    IsEligibleActionViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = EligibilityCheck
    serializer_class = EligibilityCheckSerializer

    lookup_field = 'reference'


class CaseViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Case.objects.filter(state=CASE_STATE_OPEN, provider=None)
    model = Case
    lookup_field = 'reference'
    serializer_class = CaseSerializer

    filter_backends = (
        OrderingFilter,
        SearchFilter,
    )

    ordering_fields = ('modified', 'created')
    ordering = '-modified'

    search_fields = ('personal_details__full_name',
                     'personal_details__postcode',)

    default_state_filter = CASE_STATE_OPEN
    all_states = dict(CASE_STATE_CHOICES).keys()

    def _lock_case(self, obj):
        if self.request:
            obj.lock(self.request.user)

    def pre_save(self, obj, *args, **kwargs):
        super(CaseViewSet, self).pre_save(obj, *args, **kwargs)

        user = self.request.user
        if not obj.pk and not isinstance(user, AnonymousUser):
            obj.created_by = user

    def post_save(self, obj, *args, **kwargs):
        """
        Lock the object after each save
        """
        super(CaseViewSet, self).post_save(obj, *args, **kwargs)
        self._lock_case(obj)

    def get_object(self, *args, **kwargs):
        """
        Lock the object every time it's requested
        """
        obj = super(CaseViewSet, self).get_object(*args, **kwargs)
        self._lock_case(obj)
        return obj

    @action()
    def assign(self, request, reference=None, **kwargs):
        """
        Assigns the case to a provider
        """
        obj = self.get_object()
        form = ProviderAllocationForm(request.DATA)
        if form.is_valid():
            form.save(obj, request.user)
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )


class ProviderViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Provider
    serializer_class = ProviderSerializer

    queryset = Provider.objects.active()
