import logging
from cla_provider.authentication import LegacyCHSAuthentication
from cla_provider.forms import ProviderExtractForm
from cla_provider.helpers import ProviderExtractFormatter
from core.permissions import IsProviderPermission

from django.shortcuts import get_object_or_404
from django_statsd.clients import statsd
from legalaid.permissions import IsManagerOrMePermission

from rest_framework import mixins
from rest_framework.decorators import action, link
from rest_framework.response import Response as DRFResponse

from cla_eventlog.views import BaseEventViewSet, BaseLogViewSet

from legalaid.models import Case
from legalaid.views import BaseUserViewSet, \
    BaseNestedEligibilityCheckViewSet, BaseCategoryViewSet, \
    BaseMatterTypeViewSet, BaseMediaCodeViewSet, FullPersonalDetailsViewSet, \
    BaseThirdPartyDetailsViewSet, BaseAdaptationDetailsViewSet, \
    BaseAdaptationDetailsMetadataViewSet, FullCaseViewSet, \
    BaseFeedbackViewSet, BaseCaseNotesHistoryViewSet

from diagnosis.views import BaseDiagnosisViewSet
from cla_common.constants import REQUIRES_ACTION_BY

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from .serializers import EligibilityCheckSerializer, \
    CaseSerializer, StaffSerializer, AdaptationDetailsSerializer, \
    PersonalDetailsSerializer, ThirdPartyDetailsSerializer, \
    LogSerializer, FeedbackSerializer, ExtendedEligibilityCheckSerializer, \
    CaseListSerializer, CaseNotesHistorySerializer
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
    serializer_class = CaseListSerializer
    serializer_detail_class = CaseSerializer

    queryset = Case.objects.exclude(provider=None).select_related('diagnosis', 'eligibility_check', 'personal_details')
    queryset_detail = Case.objects.exclude(provider=None).select_related(
        'eligibility_check', 'personal_details',
        'adaptation_details', 'matter_type1', 'matter_type2',
        'diagnosis', 'media_code', 'eligibility_check__category',
        'created_by'
    )

    ordering_fields = ('-requires_action_by', 'modified',
                       'personal_details__full_name', 'personal_details__postcode')

    def get_queryset(self, **kwargs):
        """
        Returns the following:
            all:
                no querystring
            new:
                only == 'new'
            opened:
                only == 'opened'
            accepted:
                only == 'accepted'
            closed:
                only == 'closed'
        """
        this_provider = get_object_or_404(
            Staff, user=self.request.user).provider
        qs = super(CaseViewSet, self).get_queryset(**kwargs).filter(
            provider=this_provider
        ).exclude(outcome_code='IRCB')

        only_param = self.request.QUERY_PARAMS.get('only')
        if only_param == 'new':
            qs = qs.filter(
                provider_viewed__isnull=True
            )
        elif only_param == 'opened':
            qs = qs.filter(
                provider_viewed__isnull=False,
                provider_accepted__isnull=True,
                provider_closed__isnull=True
            )
        elif only_param == 'accepted':
            qs = qs.filter(
                provider_accepted__isnull=False,
                provider_closed__isnull=True
            )
        elif only_param == 'closed':
            qs = qs.filter(
                provider_closed__isnull=False
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

    @link()
    def legal_help_form_extract(self, *args, **kwargs):
        case = self.get_object()
        data = {
            'case': CaseSerializer(instance=case).data,
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
        # this is to keep backward compatibility with the old system
        data = request.POST.copy()
        if 'CHSOrganisationID' not in data:
            data['CHSOrganisationID'] = data.get('CHSOrgansationID')

        form = ProviderExtractForm(data)
        if form.is_valid():
            data = form.cleaned_data
            try:
                case = Case.objects.get(reference__iexact=data['CHSCRN'])
            except Case.DoesNotExist:
                return DRFResponse({'detail': 'Not found'},
                    content_type='application/json',
                    status=404,
                    headers={
                        'Access-Control-Allow-Origin': '*'
                    })
            self.check_object_permissions(request, case)
            statsd.incr('provider_extract.exported')

            logger.info('Provider case exported',
                        extra={'USERNAME': request.user.username,
                               'POSTDATA': request.POST})

            return ProviderExtractFormatter(case).format()
        else:
            statsd.incr('provider_extract.malformed')
            return DRFResponse(form.errors, content_type='text/xml',
                               status=400,
                               headers={
                                'Access-Control-Allow-Origin': '*'
                                })


class UserViewSet(CLAProviderPermissionViewSetMixin, BaseUserViewSet):
    model = Staff
    serializer_class = StaffSerializer

    permission_classes = (CLAProviderClientIDPermission, IsManagerOrMePermission)

    def get_queryset(self):
        this_provider = get_object_or_404(
            Staff, user=self.request.user).provider
        qs = super(UserViewSet, self).get_queryset().filter(
            provider=this_provider)
        return qs


    def pre_save(self, obj):
        obj.provider = self.get_logged_in_user_model().provider

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


class CaseNotesHistoryViewSet(
    CLAProviderPermissionViewSetMixin, BaseCaseNotesHistoryViewSet
):
    serializer_class = CaseNotesHistorySerializer
