from core.drf.mixins import NestedGenericModelMixin
from django.shortcuts import get_object_or_404
from legalaid.serializers import MediaCodeSerializer

from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter, SearchFilter, \
    DjangoFilterBackend
from rest_framework.decorators import action

from cla_eventlog.views import BaseEventViewSet

from legalaid.models import Category, Case, MediaCode, MatterType, \
    PersonalDetails, AdaptationDetails
from legalaid.views import BaseUserViewSet, FormActionMixin, \
    BaseEligibilityCheckViewSet
from diagnosis.views import BaseDiagnosisViewSet
from cla_common.constants import REQUIRES_ACTION_BY

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from .serializers import CategorySerializer, \
    EligibilityCheckSerializer, CaseSerializer, StaffSerializer, \
    MatterTypeSerializer, PersonalDetailsSerializer, \
    AdaptationDetailsSerializer
from .forms import RejectCaseForm, AcceptCaseForm, CloseCaseForm


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
    BaseEligibilityCheckViewSet
):
    serializer_class = EligibilityCheckSerializer


class MatterTypeViewSet(
    CLAProviderPermissionViewSetMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = MatterType
    serializer_class = MatterTypeSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('level', 'category__code')

class MediaCodeViewSet(
    CLAProviderPermissionViewSetMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = MediaCode
    serializer_class = MediaCodeSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name', 'group__name')


class CaseViewSet(
    CLAProviderPermissionViewSetMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    FormActionMixin,
    viewsets.GenericViewSet
):
    queryset = Case.objects.exclude(provider=None)
    model = Case
    lookup_field = 'reference'
    serializer_class = CaseSerializer

    filter_backends = (
        OrderingFilter,
        SearchFilter,
    )

    search_fields = ('personal_details__full_name',
                     'personal_details__postcode',
                     'reference', 'laa_reference')

    ordering_fields = ('-requires_action_by', 'modified', 'created')
    ordering = ('-locked_by', '-modified', '-created')

    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    def get_queryset(self):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(CaseViewSet, self).get_queryset().filter(
            provider=this_provider,
            requires_action_by__in=[
                REQUIRES_ACTION_BY.PROVIDER, REQUIRES_ACTION_BY.PROVIDER_REVIEW
            ]
        )
        return qs

    def get_object(self, *args, **kwargs):
        """
        Lock the object every time it's requested
        """
        obj = super(CaseViewSet, self).get_object(*args, **kwargs)
        if self.request:
            obj.lock(self.request.user)
        return obj

    @action()
    def reject(self, request, reference=None, **kwargs):
        """
        Rejects a case
        """
        return self._form_action(request, Form=RejectCaseForm)

    @action()
    def accept(self, request, reference=None, **kwargs):
        """
        Accepts a case
        """
        return self._form_action(request, Form=AcceptCaseForm)

    @action()
    def close(self, request, reference=None, **kwargs):
        """
        Closes a case
        """
        return self._form_action(request, Form=CloseCaseForm)


class UserViewSet(CLAProviderPermissionViewSetMixin, BaseUserViewSet):
    model = Staff
    serializer_class = StaffSerializer

    def get_queryset(self):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(UserViewSet, self).get_queryset().filter(provider=this_provider)
        return qs

    def get_logged_in_user_model(self):
        return self.request.user.staff


class PersonalDetailsViewSet(CLAProviderPermissionViewSetMixin,
                             mixins.UpdateModelMixin,
                             mixins.RetrieveModelMixin,
                             NestedGenericModelMixin,
                             viewsets.GenericViewSet):
    model = PersonalDetails
    serializer_class = PersonalDetailsSerializer
    lookup_field = 'reference'

    PARENT_FIELD = 'personal_details'


class EventViewSet(CLAProviderPermissionViewSetMixin, BaseEventViewSet):
    pass


class AdaptationDetailsMetadataViewSet(CLAProviderPermissionViewSetMixin,
                                       mixins.CreateModelMixin,
                                       viewsets.GenericViewSet):
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializer

    def create(self, request, *args, **kwargs):
        self.http_method_not_allowed(request)


class AdaptationDetailsViewSet(CLAProviderPermissionViewSetMixin,
                               mixins.CreateModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.RetrieveModelMixin,
                               NestedGenericModelMixin,
                               viewsets.GenericViewSet):
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializer
    lookup_field = 'reference'
    PARENT_FIELD = 'adaptation_details'


class DiagnosisViewSet(CLAProviderPermissionViewSetMixin, BaseDiagnosisViewSet):
    pass
