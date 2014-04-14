from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_CHOICES
from cla_provider.models import Staff
from cla_provider.permissions import CLAProviderClientIDPermission
from cla_provider.serializers import CategorySerializer, \
    EligibilityCheckSerializer, CaseSerializer
from core.viewsets import DefaultStateFilterViewSetMixin
from django.shortcuts import get_object_or_404
from legalaid.models import Category, EligibilityCheck, Case
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter


class CLAProviderPermissionViewSetMixin(object):
    permission_classes = (CLAProviderClientIDPermission,)

class CategoryViewSet(CLAProviderPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

    lookup_field = 'code'

class EligibilityCheckViewSet(
    CLAProviderPermissionViewSetMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = EligibilityCheck
    serializer_class = EligibilityCheckSerializer

    lookup_field = 'reference'


class CaseViewSet(
    CLAProviderPermissionViewSetMixin,
    DefaultStateFilterViewSetMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Case.objects.exclude(provider=None)
    model = Case
    lookup_field = 'reference'
    serializer_class = CaseSerializer

    filter_backends = (
        OrderingFilter,
    )

    ordering_fields = ('modified', 'created')
    ordering = '-modified'

    default_state_filter = CASE_STATE_OPEN
    all_states = dict(CASE_STATE_CHOICES).keys()

    def get_queryset(self):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(CaseViewSet, self).get_queryset().filter(provider=this_provider)
        return qs
