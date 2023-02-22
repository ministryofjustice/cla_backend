import logging
from cla_provider.authentication import LegacyCHSAuthentication
from cla_provider.forms import ProviderExtractForm
from cla_provider.helpers import ProviderExtractFormatter
from core.permissions import IsProviderPermission
from core.drf.mixins import ClaCreateModelMixin, ClaUpdateModelMixin
from core.drf.paginator import StandardResultsSetPagination

from django.shortcuts import get_object_or_404
from legalaid.permissions import IsManagerOrMePermission

from rest_framework import mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import SearchFilter

from cla_eventlog.views import BaseEventViewSet, BaseLogViewSet

from legalaid.models import Case
from legalaid.views import (
    BaseUserViewSet,
    BaseNestedEligibilityCheckViewSet,
    BaseCategoryViewSet,
    BaseMatterTypeViewSet,
    BaseMediaCodeViewSet,
    FullPersonalDetailsViewSet,
    BaseThirdPartyDetailsViewSet,
    BaseAdaptationDetailsViewSet,
    BaseAdaptationDetailsMetadataViewSet,
    BaseContactResearchMethodViewSet,
    FullCaseViewSet,
    BaseFeedbackViewSet,
    BaseCaseNotesHistoryViewSet,
    BaseCSVUploadViewSet,
    DescCaseOrderingFilter,
)
from legalaid.serializers import ContactResearchMethodSerializerBase

from diagnosis.views import BaseDiagnosisViewSet

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from .serializers import (
    EligibilityCheckSerializer,
    CaseSerializer,
    StaffSerializer,
    AdaptationDetailsSerializer,
    PersonalDetailsSerializer,
    ThirdPartyDetailsSerializer,
    LogSerializer,
    FeedbackSerializer,
    ExtendedEligibilityCheckSerializer,
    CaseListSerializer,
    CaseNotesHistorySerializer,
    CSVUploadSerializer,
    CSVUploadDetailSerializer,
)
from .forms import RejectCaseForm, AcceptCaseForm, CloseCaseForm, SplitCaseForm, ReopenCaseForm

logger = logging.getLogger(__name__)


class CLAProviderPermissionViewSetMixin(object):
    permission_classes = (CLAProviderClientIDPermission,)

    def get_logged_in_user_model(self):
        return self.request.user.staff


class CategoryViewSet(CLAProviderPermissionViewSetMixin, BaseCategoryViewSet):
    pass


class EligibilityCheckViewSet(
    CLAProviderPermissionViewSetMixin,
    ClaUpdateModelMixin,
    mixins.RetrieveModelMixin,
    BaseNestedEligibilityCheckViewSet,
):
    serializer_class = EligibilityCheckSerializer

    # this is to fix a stupid thing in DRF where pre_save doesn't call super
    def perform_create(self, serializer):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data
        super(EligibilityCheckViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data
        super(EligibilityCheckViewSet, self).perform_update(serializer)


class MatterTypeViewSet(CLAProviderPermissionViewSetMixin, BaseMatterTypeViewSet):
    pass


class MediaCodeViewSet(CLAProviderPermissionViewSetMixin, BaseMediaCodeViewSet):
    pass


class CaseViewSet(CLAProviderPermissionViewSetMixin, FullCaseViewSet):
    serializer_class = CaseListSerializer
    serializer_detail_class = CaseSerializer

    queryset = Case.objects.exclude(provider=None).select_related("diagnosis", "eligibility_check", "personal_details")
    queryset_detail = Case.objects.exclude(provider=None).select_related(
        "eligibility_check",
        "personal_details",
        "adaptation_details",
        "matter_type1",
        "matter_type2",
        "diagnosis",
        "media_code",
        "eligibility_check__category",
        "created_by",
    )

    filter_backends = (DescCaseOrderingFilter, SearchFilter)

    ordering_fields = (
        "modified",
        "null_priority",
        "priority",
        "personal_details__full_name",
        "personal_details__postcode",
    )

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
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = (
            super(CaseViewSet, self).get_queryset(**kwargs).filter(provider=this_provider).exclude(outcome_code="IRCB")
        )

        only_param = self.request.query_params.get("only")
        if only_param == "new":
            qs = qs.filter(provider_viewed__isnull=True, provider_accepted__isnull=True, provider_closed__isnull=True)
        elif only_param == "opened":
            qs = qs.filter(provider_viewed__isnull=False, provider_accepted__isnull=True, provider_closed__isnull=True)
        elif only_param == "accepted":
            qs = qs.filter(provider_accepted__isnull=False, provider_closed__isnull=True)
        elif only_param == "closed":
            qs = qs.filter(provider_closed__isnull=False)

        return qs

    @detail_route(methods=["post"])
    def reject(self, request, reference=None, **kwargs):
        """
        Rejects a case
        """
        return self._form_action(request, Form=RejectCaseForm)

    @detail_route(methods=["post"])
    def accept(self, request, reference=None, **kwargs):
        """
        Accepts a case
        """
        return self._form_action(request, Form=AcceptCaseForm, no_body=False)

    @detail_route(methods=["post"])
    def close(self, request, reference=None, **kwargs):
        """
        Closes a case
        """
        return self._form_action(request, Form=CloseCaseForm)

    @detail_route(methods=["post"])
    def reopen(self, request, reference=None, **kwargs):
        """
        Reopens a case
        """
        return self._form_action(request, Form=ReopenCaseForm, no_body=False)

    @detail_route()
    def legal_help_form_extract(self, *args, **kwargs):
        case = self.get_object()
        data = {
            "case": CaseSerializer(instance=case).data,
            "personal_details": PersonalDetailsSerializer(instance=case.personal_details).data,
            "eligibility_check": ExtendedEligibilityCheckSerializer(instance=case.eligibility_check).data,
        }
        return DRFResponse(data)

    @detail_route(methods=["post"])
    def split(self, request, reference=None, **kwargs):
        return self._form_action(request, Form=SplitCaseForm, form_kwargs={"request": request})


class ProviderExtract(APIView):
    permission_classes = (IsProviderPermission,)
    authentication_classes = (LegacyCHSAuthentication,)

    http_method_names = [u"post", "options"]

    def options(self, request):
        """
        CORS requests begin with an OPTIONS request, which must not require
        authentication and must have CORS headers in the response.
        """
        return DRFResponse(
            self.metadata(request),
            content_type="application/json",
            status=200,
            headers={"Access-Control-Allow-Origin": "*"},
        )

    def post(self, request):
        # this is to keep backward compatibility with the old system
        data = request.POST.copy()
        if "CHSOrganisationID" not in data:
            data["CHSOrganisationID"] = data.get("CHSOrgansationID")

        form = ProviderExtractForm(data)
        if form.is_valid():
            data = form.cleaned_data
            try:
                case = Case.objects.get(reference__iexact=data["CHSCRN"])
            except Case.DoesNotExist:
                return DRFResponse(
                    {"detail": "Not found"},
                    content_type="application/json",
                    status=404,
                    headers={"Access-Control-Allow-Origin": "*"},
                )
            self.check_object_permissions(request, case)

            logger.info("Provider case exported", extra={"USERNAME": request.user.username, "POSTDATA": request.POST})

            return ProviderExtractFormatter(case).format()
        else:
            return DRFResponse(
                form.errors, content_type="text/xml", status=400, headers={"Access-Control-Allow-Origin": "*"}
            )


class UserViewSet(CLAProviderPermissionViewSetMixin, BaseUserViewSet):
    queryset = Staff.objects.all()
    model = Staff
    serializer_class = StaffSerializer

    permission_classes = (CLAProviderClientIDPermission, IsManagerOrMePermission)

    def get_queryset(self):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(UserViewSet, self).get_queryset().filter(provider=this_provider)
        return qs

    def perform_create(self, serializer):
        serializer.validated_data["provider"] = self.get_logged_in_user_model().provider
        super(UserViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        serializer.validated_data["provider"] = self.get_logged_in_user_model().provider
        super(UserViewSet, self).perform_update(serializer)


class PersonalDetailsViewSet(CLAProviderPermissionViewSetMixin, FullPersonalDetailsViewSet):
    serializer_class = PersonalDetailsSerializer


class ThirdPartyDetailsViewSet(CLAProviderPermissionViewSetMixin, BaseThirdPartyDetailsViewSet):
    serializer_class = ThirdPartyDetailsSerializer


class EventViewSet(CLAProviderPermissionViewSetMixin, BaseEventViewSet):
    pass


class AdaptationDetailsViewSet(CLAProviderPermissionViewSetMixin, BaseAdaptationDetailsViewSet):
    serializer_class = AdaptationDetailsSerializer


class AdaptationDetailsMetadataViewSet(CLAProviderPermissionViewSetMixin, BaseAdaptationDetailsMetadataViewSet):
    serializer_class = AdaptationDetailsSerializer


class ContactResearchMethodViewSet(CLAProviderPermissionViewSetMixin, BaseContactResearchMethodViewSet):
    serializer_class = ContactResearchMethodSerializerBase


class DiagnosisViewSet(CLAProviderPermissionViewSetMixin, BaseDiagnosisViewSet):
    pass


class LogViewSet(CLAProviderPermissionViewSetMixin, BaseLogViewSet):
    serializer_class = LogSerializer


class FeedbackViewSet(CLAProviderPermissionViewSetMixin, BaseFeedbackViewSet, ClaCreateModelMixin):
    serializer_class = FeedbackSerializer

    filter_backends = (OrderingFilter,)
    ordering = ("-created",)

    def perform_create(self, serializer):
        serializer.validated_data["case"] = self.get_parent_object()
        serializer.validated_data["created_by"] = Staff.objects.get(user=self.request.user)
        super(FeedbackViewSet, self).perform_create(serializer)


class CSVUploadViewSet(CLAProviderPermissionViewSetMixin, BaseCSVUploadViewSet):
    serializer_class = CSVUploadSerializer
    serializer_detail_class = CSVUploadDetailSerializer

    ordering = ("-month",)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(CSVUploadViewSet, self).get_queryset(*args, **kwargs).filter(provider=this_provider)
        return qs

    def set_provider_user(self, serializer):
        user = self.get_logged_in_user_model()
        serializer.validated_data["provider"] = user.provider
        serializer.validated_data["created_by"] = user

    def perform_create(self, serializer):
        self.set_provider_user(serializer)
        return super(CSVUploadViewSet, self).perform_create(serializer)

    def perform_update(self, serializer):
        self.set_provider_user(serializer)
        return super(CSVUploadViewSet, self).perform_update(serializer)


class CaseNotesHistoryViewSet(CLAProviderPermissionViewSetMixin, BaseCaseNotesHistoryViewSet):
    serializer_class = CaseNotesHistorySerializer
