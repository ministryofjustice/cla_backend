from django.shortcuts import get_object_or_404

from rest_framework import mixins
from rest_framework.decorators import action

from cla_eventlog.views import BaseEventViewSet, BaseLogViewSet

from legalaid.models import Case
from legalaid.views import BaseUserViewSet, \
    BaseNestedEligibilityCheckViewSet, BaseCategoryViewSet, \
    BaseMatterTypeViewSet, BaseMediaCodeViewSet, FullPersonalDetailsViewSet, \
    BaseThirdPartyDetailsViewSet, BaseAdaptationDetailsViewSet, \
    BaseAdaptationDetailsMetadataViewSet, FullCaseViewSet

from diagnosis.views import BaseDiagnosisViewSet
from cla_common.constants import REQUIRES_ACTION_BY

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from .serializers import EligibilityCheckSerializer, \
    CaseSerializer, StaffSerializer, AdaptationDetailsSerializer, \
    PersonalDetailsSerializer, ThirdPartyDetailsSerializer, \
    LogSerializer
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
    CLAProviderPermissionViewSetMixin, FullCaseViewSet
):
    serializer_class = CaseSerializer
    queryset = Case.objects.exclude(provider=None)

    ordering_fields = ('-requires_action_by', 'modified', 'personal_details__full_name', 'personal_details__postcode', 'adaptation_details__language', 'thirdparty_details__personal_details__full_name')

    def get_queryset(self):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(CaseViewSet, self).get_queryset().filter(
            provider=this_provider,
            requires_action_by__in=[
                REQUIRES_ACTION_BY.PROVIDER, REQUIRES_ACTION_BY.PROVIDER_REVIEW
            ]
        )
        return qs

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
        return self._form_action(request, Form=AcceptCaseForm, no_body=False)

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


class LogViewSet(CLAProviderPermissionViewSetMixin, BaseLogViewSet):
    serializer_class = LogSerializer
