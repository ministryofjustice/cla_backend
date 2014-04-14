import json
from call_centre.forms import ProviderAllocationForm
from call_centre.permissions import CallCentreClientIDPermission
from call_centre.serializers import EligibilityCheckSerializer, CategorySerializer, \
    CaseSerializer, ProviderSerializer
from cla_common.constants import CASE_STATE_CLOSED, CASE_STATE_OPEN, \
    CASE_STATE_CHOICES
from cla_provider.models import Provider
from core.viewsets import IsEligibleActionViewSetMixin
from django import http
from django.contrib.auth.models import AnonymousUser
from legalaid.models import Category, EligibilityCheck, Case
from rest_framework import viewsets, mixins
# from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter


class CallCentrePermissionsViewSetMixin(object):
    permission_classes = (CallCentreClientIDPermission,)

class CategoryViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

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

    def pre_save(self, obj):
        user = self.request.user
        if not obj.pk and not isinstance(user, AnonymousUser):
            obj.created_by = user


class ProviderViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Provider
    serializer_class = ProviderSerializer

