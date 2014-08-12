from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action

from cla_eventlog.views import BaseEventViewSet

from legalaid.models import Case
from legalaid.views import BaseUserViewSet, FormActionMixin, \
    BaseNestedEligibilityCheckViewSet, BaseCategoryViewSet, \
    BaseMatterTypeViewSet, BaseMediaCodeViewSet, FullPersonalDetailsViewSet, \
    BaseThirdPartyDetailsViewSet, BaseAdaptationDetailsViewSet, \
    BaseAdaptationDetailsMetadataViewSet

from diagnosis.views import BaseDiagnosisViewSet
from cla_common.constants import REQUIRES_ACTION_BY

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from .serializers import EligibilityCheckSerializer, \
    CaseSerializer, StaffSerializer, AdaptationDetailsSerializer, \
    PersonalDetailsSerializer, ThirdPartyDetailsSerializer
from .forms import RejectCaseForm, AcceptCaseForm, CloseCaseForm


class CLAProviderPermissionViewSetMixin(object):
    permission_classes = (CLAProviderClientIDPermission,)


class CategoryViewSet(CLAProviderPermissionViewSetMixin, BaseCategoryViewSet):
    pass


class EligibilityCheckViewSet(
    CLAProviderPermissionViewSetMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    BaseNestedEligibilityCheckViewSet
):
    serializer_class = EligibilityCheckSerializer

    # this is to fix a stupid thing in DRF where pre_save doesn't call super
    def pre_save(self, obj):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data


class MatterTypeViewSet(
    CLAProviderPermissionViewSetMixin, BaseMatterTypeViewSet
):
    pass


class MediaCodeViewSet(
    CLAProviderPermissionViewSetMixin, BaseMediaCodeViewSet
):
    pass


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


class PersonalDetailsViewSet(
    CLAProviderPermissionViewSetMixin,
    FullPersonalDetailsViewSet
):
    serializer_class = PersonalDetailsSerializer


class ThirdPartyDetailsViewSet(
    CLAProviderPermissionViewSetMixin,
    BaseThirdPartyDetailsViewSet
):
    serializer_class = ThirdPartyDetailsSerializer


class EventViewSet(CLAProviderPermissionViewSetMixin, BaseEventViewSet):
    pass


class AdaptationDetailsViewSet(
    CLAProviderPermissionViewSetMixin, BaseAdaptationDetailsViewSet
):
    serializer_class = AdaptationDetailsSerializer


class AdaptationDetailsMetadataViewSet(
    CLAProviderPermissionViewSetMixin, BaseAdaptationDetailsMetadataViewSet
):
    serializer_class = AdaptationDetailsSerializer


class DiagnosisViewSet(
    CLAProviderPermissionViewSetMixin, BaseDiagnosisViewSet
):
    pass
