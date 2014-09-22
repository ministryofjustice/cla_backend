import logging
from cla_provider.authentication import LegacyCHSAuthentication
from cla_provider.forms import ProviderExtractForm
from cla_provider.helpers import ProviderExtractFormatter
from core.permissions import IsProviderPermission

from django.shortcuts import get_object_or_404
from django_statsd.clients import statsd

from rest_framework import mixins
from rest_framework.decorators import action, link
from rest_framework.response import Response as DRFResponse

from cla_eventlog.views import BaseEventViewSet, BaseLogViewSet

from legalaid.models import Case
from legalaid.views import BaseUserViewSet, \
    BaseNestedEligibilityCheckViewSet, BaseCategoryViewSet, \
    BaseMatterTypeViewSet, BaseMediaCodeViewSet, FullPersonalDetailsViewSet, \
    BaseThirdPartyDetailsViewSet, BaseAdaptationDetailsViewSet, \
    BaseAdaptationDetailsMetadataViewSet, FullCaseViewSet, BaseFeedbackViewSet

from diagnosis.views import BaseDiagnosisViewSet
from cla_common.constants import REQUIRES_ACTION_BY

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from .serializers import EligibilityCheckSerializer, \
    CaseSerializer, StaffSerializer, AdaptationDetailsSerializer, \
    PersonalDetailsSerializer, ThirdPartyDetailsSerializer, \
    LogSerializer, FeedbackSerializer, ExtendedEligibilityCheckSerializer
from .forms import RejectCaseForm, AcceptCaseForm, CloseCaseForm, SplitCaseForm

logger = logging.getLogger(__name__)

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

    ordering_fields = ('-requires_action_by', 'modified',
                       'personal_details__full_name', 'personal_details__postcode')

    def get_queryset(self):
        this_provider = get_object_or_404(
            Staff, user=self.request.user).provider
        qs = super(CaseViewSet, self).get_queryset().filter(
            provider=this_provider,
            requires_action_by__in=[
                REQUIRES_ACTION_BY.PROVIDER, REQUIRES_ACTION_BY.PROVIDER_REVIEW
            ]
        )

        show_new = self.request.QUERY_PARAMS.get('new', '1') == '1'
        show_viewed = self.request.QUERY_PARAMS.get('viewed', '1') == '1'
        show_accepted = self.request.QUERY_PARAMS.get('accepted', '1') == '1'

        if not show_new:
            qs = qs.filter(provider_viewed__isnull=False)

        if not show_viewed:
            qs = qs.filter(provider_viewed__isnull=True)

        if not show_accepted:
            qs = qs.exclude(outcome_code='SPOP')

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

    @link()
    def legal_help_form_extract(self, *args, **kwargs):
        case = self.get_object()
        data = {
            'personal_details': PersonalDetailsSerializer(
                instance=case.personal_details
            ).data,
            'eligibility_check': ExtendedEligibilityCheckSerializer(
                instance=case.eligibility_check
            ).data
        }
        return DRFResponse(data)

    @action()
    def split(self, request, reference=None, **kwargs):
        return self._form_action(
            request, Form=SplitCaseForm, form_kwargs={
                'request': request
            }
        )


class ProviderExtract(APIView):
    permission_classes = (IsProviderPermission,)
    authentication_classes = (LegacyCHSAuthentication,)

    http_method_names = [u'post']

    def post(self, request):
        form = ProviderExtractForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            case = get_object_or_404(Case, reference__iexact=data['CHSCRN'])
            self.check_object_permissions(request, case)
            statsd.incr('provider_extract.exported')

            logger.info('Provider case exported',
                        extra={'USERNAME': request.user.username,
                               'POSTDATA': request.POST})

            return ProviderExtractFormatter(case).format()
        else:
            statsd.incr('provider_extract.malformed')
            return DRFResponse(form.errors, content_type='text/xml', status=400)


class UserViewSet(CLAProviderPermissionViewSetMixin, BaseUserViewSet):
    model = Staff
    serializer_class = StaffSerializer

    def get_queryset(self):
        this_provider = get_object_or_404(
            Staff, user=self.request.user).provider
        qs = super(UserViewSet, self).get_queryset().filter(
            provider=this_provider)
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


class FeedbackViewSet(CLAProviderPermissionViewSetMixin,
                      BaseFeedbackViewSet,
                      mixins.CreateModelMixin):
    serializer_class = FeedbackSerializer

    filter_backends = (
        OrderingFilter,
    )
    ordering = ('-created')

    def pre_save(self, obj):
        if not obj.pk:
            obj.case = self.get_parent_object()
            obj.created_by = Staff.objects.get(user=self.request.user)
        super(FeedbackViewSet, self).pre_save(obj)
