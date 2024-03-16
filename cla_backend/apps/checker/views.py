from django.http import Http404, JsonResponse
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response as DRFResponse
from rest_framework.exceptions import ParseError

from core.models import get_web_user
from core.drf.mixins import ClaCreateModelMixin, ClaUpdateModelMixin
from core.drf.viewsets import CompatGenericViewSet
from diagnosis.views import DiagnosisModelMixin

from knowledgebase.views import BaseArticleViewSet, ArticleCategoryFilter

from legalaid.models import Case
from legalaid.views import BaseCategoryViewSet, BaseEligibilityCheckViewSet, BaseCaseLogMixin
from cla_common.constants import CASE_SOURCE
from checker.call_centre_availability import get_available_slots
from cla_common.call_centre_availability import SLOT_INTERVAL_MINS

from .models import ReasonForContacting
from .serializers import (
    EligibilityCheckSerializer,
    CaseSerializer,
    CheckerDiagnosisSerializer,
    ReasonForContactingSerializer,
)
from .forms import WebCallMeBackForm

logger = __import__("logging").getLogger(__name__)


class PublicAPIViewSetMixin(object):
    permission_classes = (AllowAny,)


class CategoryViewSet(PublicAPIViewSetMixin, BaseCategoryViewSet):
    """
    This returns a list of all valid categories in the system.
    """

    pass


class ArticleCategoryNameFilter(ArticleCategoryFilter):
    class Meta(ArticleCategoryFilter.Meta):
        fields = ("article_category__name",)


class ArticleViewSet(PublicAPIViewSetMixin, BaseArticleViewSet):

    filter_class = ArticleCategoryNameFilter


class EligibilityCheckViewSet(
    PublicAPIViewSetMixin,
    ClaCreateModelMixin,
    ClaUpdateModelMixin,
    mixins.RetrieveModelMixin,
    BaseEligibilityCheckViewSet,
):
    serializer_class = EligibilityCheckSerializer

    def get_request_user(self):
        return get_web_user()

    @detail_route(methods=["post"])
    def is_eligible(self, request, *args, **kwargs):
        obj = self.get_object()

        logger.info("Eligibility check - load form")
        response, ec, reasons = obj.get_eligibility_state()
        return DRFResponse({"is_eligible": response, "reasons": reasons})

    @detail_route()
    def case_ref(self, request, *args, **kwargs):
        try:
            return DRFResponse({"reference": self.get_object().case.reference})
        except AttributeError:
            raise Http404


class CaseViewSet(PublicAPIViewSetMixin, BaseCaseLogMixin, ClaCreateModelMixin, CompatGenericViewSet):

    queryset = Case.objects.all()
    model = Case
    serializer_class = CaseSerializer

    def perform_create(self, serializer):
        created_by = serializer.validated_data.get("created_by", None)
        if not created_by:
            serializer.validated_data["created_by"] = get_web_user()
        serializer.validated_data["source"] = CASE_SOURCE.WEB
        return super(CaseViewSet, self).perform_create(serializer)

    def post_save(self, obj, created=False):
        super(CaseViewSet, self).post_save(obj, created=created)

        if created and obj.requires_action_at:
            form = WebCallMeBackForm(case=obj, data={}, requires_action_at=obj.requires_action_at)

            if form.is_valid():
                form.save(obj.created_by)

    def get_log_notes(self, obj):
        return "Case created digitally"


class DiagnosisViewSet(
    PublicAPIViewSetMixin,
    DiagnosisModelMixin,
    ClaCreateModelMixin,
    ClaUpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    CompatGenericViewSet,
):
    serializer_class = CheckerDiagnosisSerializer

    def try_to_original_obj(self):
        try:
            self._original_obj = self.get_object()
        except AssertionError:
            pass

    def perform_create(self, serializer):
        self.try_to_original_obj()
        # The use of DiagnosisModelMixin instead DiagnosisViewSet to call super is on purpose
        # As the previous code was trying to bypass the DiagnosisModelMixin pre_save hooks
        return super(DiagnosisModelMixin, self).perform_create(serializer)

    def perform_update(self, serializer):
        self.try_to_original_obj()
        # The use of DiagnosisModelMixin instead DiagnosisViewSet to call super is on purpose
        # As the previous code was trying to bypass the DiagnosisModelMixin pre_save hooks
        super(DiagnosisModelMixin, self).perform_update(serializer)

    def get_current_user(self):
        return get_web_user()


class ReasonForContactingViewSet(
    PublicAPIViewSetMixin, ClaCreateModelMixin, ClaUpdateModelMixin, CompatGenericViewSet
):
    queryset = ReasonForContacting.objects.all()
    model = ReasonForContacting
    serializer_class = ReasonForContactingSerializer
    lookup_field = "reference"

    def perform_update(self, serializer):
        if "reasons" in serializer.validated_data:
            serializer.instance.reasons.all().delete()
        super(ReasonForContactingViewSet, self).perform_update(serializer)


class CallbackTimeSlotViewSet(PublicAPIViewSetMixin, APIView):
    def get(self, request, *args, **kwargs):
        """Get router for the callback timeslot API.

        Args:
            string: QueryParameter - num_days: How many days of callback times are requested, defaults to 7- has a hard limit of between 1 and 31.
            string: QueryParameter - third_party_callback: If the callback is for a third party no capacity rules apply, defaults to True.

        Returns:
            json: Json object containing a list of valid callback datetimes.
        """

        try:
            requested_num_days = int(request.GET.get('num_days', default=7))
            num_days = max(min(requested_num_days, 31), 1)
        except ValueError:
            raise ParseError(detail="Invalid value for num_days sent to callback_timeslots endpoint")

        try:
            third_party_callback = bool(request.GET.get('third_party_callback', default=False))
        except ValueError:
            raise ParseError(detail="Invalid value for third_party_callback sent to callback_timeslots endpoint")

        slots = get_available_slots(num_days, third_party_callback)
        response = {"slot_duration_minutes": SLOT_INTERVAL_MINS,
                    "slots": slots}
        return JsonResponse(response)
