import json

from core.drf.exceptions import ConflictException
from django import forms
from django.db import connection, transaction, IntegrityError
from django.utils.crypto import get_random_string
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework_extensions.mixins import DetailSerializerMixin

from core.utils import format_patch
from core.drf.mixins import (
    NestedGenericModelMixin,
    JsonPatchViewSetMixin,
    FormActionMixin,
    ClaCreateModelMixin,
    ClaUpdateModelMixin,
    ClaRetrieveModelMixinWithSelfInstance,
)
from core.drf.viewsets import CompatGenericViewSet
from core.drf.paginator import StandardResultsSetPagination, CaseNotesHistoryResultsSetPagination
from legalaid.permissions import IsManagerOrMePermission
from cla_eventlog import event_registry
from cla_auth.models import AccessAttempt
from .serializers import (
    CategorySerializerBase,
    MatterTypeSerializerBase,
    MediaCodeSerializerBase,
    PersonalDetailsSerializerFull,
    ThirdPartyDetailsSerializerBase,
    AdaptationDetailsSerializerBase,
    CaseSerializerBase,
    FeedbackSerializerBase,
    CaseNotesHistorySerializerBase,
    CSVUploadSerializerBase,
    EODDetailsSerializerBase,
    ContactResearchMethodSerializerBase,
)
from cla_provider.models import Feedback, CSVUpload
from .models import (
    Case,
    Category,
    EligibilityCheck,
    MatterType,
    MediaCode,
    PersonalDetails,
    ThirdPartyDetails,
    AdaptationDetails,
    CaseNotesHistory,
    EODDetails,
    ContactResearchMethod,
)


class CaseFormActionMixin(FormActionMixin):
    """
    This is for backward compatibility
    """

    FORM_ACTION_OBJ_PARAM = "case"


class PasswordResetForm(forms.Form):

    new_password = forms.CharField(required=True, min_length=10)
    old_password = forms.CharField(required=False)

    def __init__(self, case=None, *args, **kwargs):
        self.action_user = kwargs.pop("action_user")
        self.reset_user = kwargs.pop("reset_user")

        super(PasswordResetForm, self).__init__(*args, **kwargs)

        if self.action_user == self.reset_user:
            self.fields["old_password"].required = True

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if self.action_user == self.reset_user:
            # changing own password
            if not self.reset_user.check_password(old_password):
                raise PermissionDenied({"__all__": ["Old password doesn't match."]})
        return old_password

    def save(self, _):
        new_password = self.cleaned_data["new_password"]
        self.reset_user.set_password(new_password)
        self.reset_user.save()


class BaseUserViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, ClaCreateModelMixin, CaseFormActionMixin, CompatGenericViewSet
):
    permission_classes = (IsManagerOrMePermission,)

    me_lookup_url_kwargs = "me"
    lookup_field = "user__username"

    def get_queryset(self):
        qs = super(BaseUserViewSet, self).get_queryset()
        return qs.filter(user__is_active=True)

    def get_logged_in_user_model(self):
        raise NotImplementedError()

    def get_object(self, *args, **kwargs):
        """
        Lock the object every time it's requested
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup = self.kwargs.get(lookup_url_kwarg, None)

        # for now, you can only access to the user/me/ object, for security
        # reasons. We'll probably change this in the future to allow service
        # managers to add/update/delete users from their area.
        # logged_in_user_model = self.get_logged_in_user_model()

        if lookup == self.me_lookup_url_kwargs:
            self.kwargs[lookup_url_kwarg] = self.request.user.username

        obj = super(BaseUserViewSet, self).get_object(*args, **kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    @detail_route(methods=["post"])
    def password_reset(self, request, *args, **kwargs):
        user = self.get_object().user
        try:
            return self._form_action(
                request, PasswordResetForm, no_body=True, form_kwargs={"action_user": request.user, "reset_user": user}
            )
        except PermissionDenied as pd:
            return DRFResponse(pd.detail, status=status.HTTP_403_FORBIDDEN)

    @detail_route(methods=["post"])
    def reset_lockout(self, request, *args, **kwargs):
        logged_in_user_model = self.get_logged_in_user_model()
        if not logged_in_user_model.is_manager:
            raise PermissionDenied()

        user = self.get_object().user
        AccessAttempt.objects.delete_for_username(user.username)
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        if not self.get_logged_in_user_model().is_manager:
            raise PermissionDenied()
        return super(BaseUserViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.check_object_permissions(request, None)
        return super(BaseUserViewSet, self).create(request, *args, **kwargs)


class BaseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    model = Category
    serializer_class = CategorySerializerBase

    lookup_field = "code"


class BaseEligibilityCheckViewSet(JsonPatchViewSetMixin, CompatGenericViewSet):
    queryset = EligibilityCheck.objects.all()
    model = EligibilityCheck
    lookup_field = "reference"

    @detail_route()
    def validate(self, request, **kwargs):
        obj = self.get_object()
        return DRFResponse(obj.validate())

    @detail_route(methods=["post"])
    def is_eligible(self, request, *args, **kwargs):
        obj = self.get_object()

        response, ec, reasons = obj.get_eligibility_state()
        return DRFResponse({"is_eligible": response})

    def get_means_test_event_kwargs(self, kwargs):
        return kwargs

    def get_request_user(self):
        return self.request.user

    def create_means_test_log(self, obj, created):
        try:
            obj.case
        except Case.DoesNotExist:
            return

        user = self.get_request_user()

        means_test_event = event_registry.get_event("means_test")()
        status = "changed" if not created else "created"
        kwargs = {"created_by": user, "status": status, "context": {"state": obj.state}}
        kwargs = self.get_means_test_event_kwargs(kwargs)
        means_test_event.process(obj.case, **kwargs)

    def post_save(self, obj, created=False, **kwargs):
        super(BaseEligibilityCheckViewSet, self).post_save(obj, created=created)

        self.create_means_test_log(obj, created=created)

        return obj


class BaseNestedEligibilityCheckViewSet(NestedGenericModelMixin, BaseEligibilityCheckViewSet):

    PARENT_FIELD = "eligibility_check"

    def get_means_test_event_kwargs(self, kwargs):
        patch = self.jsonpatch

        kwargs.update({"patch": json.dumps(patch), "notes": format_patch(patch["forwards"])})
        return kwargs


class BaseMatterTypeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, CompatGenericViewSet):
    queryset = MatterType.objects.all()
    model = MatterType
    serializer_class = MatterTypeSerializerBase

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("level", "category__code")


class BaseMediaCodeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, CompatGenericViewSet):
    queryset = MediaCode.objects.all()
    model = MediaCode
    serializer_class = MediaCodeSerializerBase

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("name", "group__name")


class BaseContactResearchMethodViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, CompatGenericViewSet):
    queryset = ContactResearchMethod.objects.all()
    model = ContactResearchMethod
    serializer_class = ContactResearchMethodSerializerBase

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("method",)


class FullPersonalDetailsViewSet(
    ClaCreateModelMixin, ClaUpdateModelMixin, mixins.RetrieveModelMixin, NestedGenericModelMixin, CompatGenericViewSet
):
    queryset = PersonalDetails.objects.all()
    model = PersonalDetails
    serializer_class = PersonalDetailsSerializerFull
    lookup_field = "reference"

    PARENT_FIELD = "personal_details"


class BaseThirdPartyDetailsViewSet(
    ClaCreateModelMixin, ClaUpdateModelMixin, mixins.RetrieveModelMixin, NestedGenericModelMixin, CompatGenericViewSet
):
    queryset = ThirdPartyDetails.objects.all()
    model = ThirdPartyDetails
    serializer_class = ThirdPartyDetailsSerializerBase
    lookup_field = "reference"
    PARENT_FIELD = "thirdparty_details"


class BaseAdaptationDetailsViewSet(
    ClaCreateModelMixin, ClaUpdateModelMixin, mixins.RetrieveModelMixin, NestedGenericModelMixin, CompatGenericViewSet
):
    queryset = AdaptationDetails.objects.all()
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializerBase
    lookup_field = "reference"
    PARENT_FIELD = "adaptation_details"


class BaseAdaptationDetailsMetadataViewSet(ClaCreateModelMixin, CompatGenericViewSet):
    queryset = AdaptationDetails.objects.all()
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializerBase

    def create(self, request, *args, **kwargs):
        self.http_method_not_allowed(request)


class BaseEODDetailsViewSet(
    ClaCreateModelMixin, ClaUpdateModelMixin, mixins.RetrieveModelMixin, NestedGenericModelMixin, CompatGenericViewSet
):
    queryset = EODDetails.objects.all()
    model = EODDetails
    serializer_class = EODDetailsSerializerBase
    lookup_field = "reference"
    PARENT_FIELD = "eod_details"

    def perform_update(self, serializer):
        if isinstance(serializer.instance, EODDetails):
            serializer.instance.categories.all().delete()

        serializer.validated_data["case"] = Case.objects.get(reference=self.kwargs.get("case_reference"))
        super(BaseEODDetailsViewSet, self).perform_update(serializer)

    def perform_create(self, serializer):
        serializer.validated_data["case"] = Case.objects.get(reference=self.kwargs.get("case_reference"))
        return super(BaseEODDetailsViewSet, self).perform_create(serializer)

    def post_save(self, obj, created=False):
        # Putting back this terrible work around as we need more time to refactor
        # core.drf.mixins.NestedGenericModelMixin.post_save not to throw a MethodNotAllowed if parent relationship is
        # already set
        return super(BaseEODDetailsViewSet, self).post_save(obj, False)


class BaseCaseOrderingFilter(OrderingFilter):

    default_modified = "modified"

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if isinstance(ordering, basestring):
            if "," in ordering:
                ordering = ordering.split(",")
            else:
                ordering = [ordering]

        if "requires_action_at" not in ordering:
            ordering.append("requires_action_at")

        if "modified" not in ordering:
            ordering.append(self.default_modified)

        return queryset.order_by(*ordering)


class AscCaseOrderingFilter(BaseCaseOrderingFilter):
    default_modified = "modified"


class DescCaseOrderingFilter(BaseCaseOrderingFilter):
    default_modified = "-modified"


class BaseCaseLogMixin(object):
    def get_log_notes(self, obj):
        raise NotImplementedError()

    def get_log_context(self, obj):
        context = {}
        if obj.eligibility_check:
            context["eligibility_state"] = obj.eligibility_check.state
        return context

    def post_save(self, obj, created=False):
        super(BaseCaseLogMixin, self).post_save(obj, created=created)

        if created:
            event = event_registry.get_event("case")()
            event.process(
                obj,
                status="created",
                created_by=obj.created_by,
                notes=self.get_log_notes(obj),
                context=self.get_log_context(obj),
            )


class FullCaseViewSet(
    DetailSerializerMixin,
    ClaUpdateModelMixin,
    ClaRetrieveModelMixinWithSelfInstance,
    mixins.ListModelMixin,
    CaseFormActionMixin,
    CompatGenericViewSet,
):
    queryset = Case.objects.all()
    model = Case
    lookup_field = "reference"
    lookup_regex = r"[A-Z|\d]{2}-\d{4}-\d{4}"

    serializer_class = CaseSerializerBase
    pagination_class = StandardResultsSetPagination

    filter_backends = (AscCaseOrderingFilter,)

    ordering_fields = (
        "modified",
        "personal_details__full_name",
        "requires_action_at",
        "personal_details__date_of_birth",
        "personal_details__postcode",
        "eligibility_check__category__name",
        "priority",
        "null_priority",
        "flagged_with_eod",
        "organisation__name",
    )
    ordering = ["-priority"]

    FLAGGED_WITH_EOD_SQL = """
    SELECT COUNT(id) > 0 FROM legalaid_eoddetails
    WHERE legalaid_case.id = legalaid_eoddetails.case_id
    AND (
        (
          legalaid_eoddetails.notes IS NOT NULL
          AND length(legalaid_eoddetails.notes) > 0
        ) OR (
          SELECT COUNT(id) > 0
            FROM legalaid_eoddetailscategory
            WHERE legalaid_eoddetailscategory.eod_details_id=legalaid_eoddetails.id
        )
    )
    """

    def get_search_terms(self):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = self.request.query_params.get("search", "")
        return params.replace(",", " ").split()

    def get_temporary_view_name(self):
        return "case_search_view_{}".format(get_random_string())

    def list(self, request, *args, **kwargs):
        try:
            return super(FullCaseViewSet, self).list(request, *args, **kwargs)
        finally:
            if hasattr(request, "temp_view_name"):
                try:
                    with connection.cursor() as cursor:
                        cursor.execute('DROP VIEW "{view_name}"'.format(view_name=self.request.temp_view_name))
                except Exception:
                    pass  # whatever, it won't survive session end

    def filter_queryset(self, queryset):
        queryset = super(FullCaseViewSet, self).filter_queryset(queryset)
        search_terms = self.get_search_terms()

        if not search_terms:
            return queryset

        select_sql = """
            (SELECT c.id FROM legalaid_case c
                LEFT OUTER JOIN legalaid_personaldetails pd ON
                c.personal_details_id=pd.id WHERE {where_clause})
            """

        case_where_sql = """
            UPPER(c.reference::text) LIKE UPPER(%s)
            OR UPPER(c.laa_reference::text) LIKE UPPER(%s)
            OR UPPER(c.search_field::text) LIKE UPPER(%s)
            """

        personal_details_where_sql = """
            UPPER(pd.full_name::text) LIKE UPPER(%s)
            OR UPPER(pd.postcode::text) LIKE UPPER(%s)
            OR UPPER(pd.street::text) LIKE UPPER(%s)
            OR UPPER(pd.search_field::text) LIKE UPPER(%s)
            """

        number_of_placeholders = 7
        unions = []
        params = []
        for search_term in search_terms:
            unions.append(
                "({})".format(
                    " UNION ".join(
                        [
                            select_sql.format(where_clause=case_where_sql),
                            select_sql.format(where_clause=personal_details_where_sql),
                        ]
                    )
                )
            )
            for _ in range(number_of_placeholders):
                params.append(u"%{}%".format(search_term))

        subquery = " INTERSECT ".join(unions)

        self.request.temp_view_name = self.get_temporary_view_name()
        create_view_sql = 'CREATE TEMPORARY VIEW "{view_name}" AS {query}'.format(
            view_name=self.request.temp_view_name, query=subquery
        )

        with connection.cursor() as cursor:
            cursor.execute(create_view_sql, params)

        return queryset.extra(
            tables=[self.request.temp_view_name],
            where=['"legalaid_case"."id"="{}"."id"'.format(self.request.temp_view_name)],
        )

    def get_queryset(self, **kwargs):
        qs = super(FullCaseViewSet, self).get_queryset(**kwargs)
        person_ref_param = self.request.query_params.get("person_ref", None)
        dashboard_param = self.request.query_params.get("dashboard", None)

        if person_ref_param:
            qs = qs.filter(personal_details__reference=person_ref_param)
        elif dashboard_param:
            qs = self.get_dashboard_qs(qs)
        qs = qs.extra(
            select={
                "null_priority": """CASE
                    WHEN legalaid_case.outcome_code IS NULL THEN 1
                    ELSE 0
                END""",
                "priority": """CASE legalaid_case.outcome_code
                        WHEN 'PCB' THEN 10
                        WHEN 'REF-EXT' THEN 8
                        WHEN 'IRCB' THEN 7
                        WHEN 'MIS' THEN 6
                        WHEN 'COI' THEN 5
                        WHEN 'CB1' THEN 4
                        WHEN 'CB2' THEN 3
                        WHEN 'CB3' THEN 2
                        ELSE 1
                    END""",
                "rejected": """CASE
                    WHEN legalaid_case.outcome_code IN (
                        'COI', 'MIS')
                    THEN 1
                    ELSE 0
                END""",
                "flagged_with_eod": self.FLAGGED_WITH_EOD_SQL,
            }
        )
        # LGA-1773 can no longer pass queryset to get_object > drf 3.0,
        # Check flag to allow select_related in parent viewset from NestedGenericModelMixin
        if hasattr(self, "do_select_related") and self.do_select_related:
            qs = qs.select_related(None)
        return qs

    def get_dashboard_qs(self, qs):
        return qs

    def retrieve(self, request, *args, **kwargs):
        resp = super(FullCaseViewSet, self).retrieve(request, *args, **kwargs)

        event = event_registry.get_event("case")()
        event.process(self.instance, status="viewed", created_by=request.user, notes="Case viewed")

        return resp

    def perform_update(self, serializer):
        previous_notes = serializer.instance.notes
        previous_provider_notes = serializer.instance.provider_notes
        previous_complaint_flag = serializer.instance.complaint_flag

        super(FullCaseViewSet, self).perform_update(serializer)
        obj = self.get_object()
        if obj.pk:
            notes = serializer.validated_data.get("notes", None)
            if notes and notes != previous_notes:
                cnh = CaseNotesHistory(case=obj)
                cnh.operator_notes = obj.notes
                cnh.created_by = self.request.user
                cnh.save()

            provider_notes = serializer.validated_data.get("provider_notes", None)
            if provider_notes and provider_notes != previous_provider_notes:
                cpnh = CaseNotesHistory(case=obj)
                cpnh.provider_notes = obj.provider_notes
                cpnh.created_by = self.request.user
                cpnh.save()

            complaint_flag = serializer.validated_data.get("complaint_flag", None)
            if complaint_flag and complaint_flag != previous_complaint_flag:
                event = event_registry.get_event("case")()
                event.process(
                    obj,
                    status="complaint_flag_toggled",
                    created_by=self.request.user,
                    notes="Complaint flag toggled: %s" % obj.complaint_flag,
                )


class BaseFeedbackViewSet(
    NestedGenericModelMixin,
    mixins.ListModelMixin,
    ClaUpdateModelMixin,
    mixins.RetrieveModelMixin,
    CompatGenericViewSet,
):
    queryset = Feedback.objects.all()
    model = Feedback
    serializer_class = FeedbackSerializerBase
    PARENT_FIELD = "provider_feedback"
    lookup_field = "reference"


class BaseCSVUploadReadOnlyViewSet(
    DetailSerializerMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, CompatGenericViewSet
):
    queryset = CSVUpload.objects.all()
    model = CSVUpload

    serializer_class = CSVUploadSerializerBase
    serializer_detail_class = CSVUploadSerializerBase

    filter_backends = (OrderingFilter,)


class BaseCSVUploadViewSet(
    DetailSerializerMixin,
    mixins.ListModelMixin,
    ClaCreateModelMixin,
    ClaUpdateModelMixin,
    mixins.RetrieveModelMixin,
    CompatGenericViewSet,
):
    queryset = CSVUpload.objects.all()
    model = CSVUpload
    serializer_class = CSVUploadSerializerBase
    serializer_detail_class = CSVUploadSerializerBase

    filter_backends = (OrderingFilter,)

    def create(self, request, *args, **kwargs):
        try:
            return super(BaseCSVUploadViewSet, self).create(request, *args, **kwargs)
        except IntegrityError:
            raise ConflictException("Upload already exists for given month. Try overwriting.")

    def update(self, request, *args, **kwargs):
        if request.method.upper() == u"PATCH":
            # Don't allow PATCH because they should DELETE+POST or PUT
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super(BaseCSVUploadViewSet, self).update(request, *args, **kwargs)


class PaginatorWithExtraItem(CaseNotesHistoryResultsSetPagination):
    """
    Same as the Paginator but it will return one more item than expected.
    Used for endpoints that need to diff elements.
    """

    extra_num = 1

    def get_page_size(self, request):
        return super(PaginatorWithExtraItem, self).get_page_size(request) + 1


class BaseCaseNotesHistoryViewSet(NestedGenericModelMixin, mixins.ListModelMixin, CompatGenericViewSet):
    PARENT_FIELD = "casenoteshistory_set"
    lookup_field = "reference"
    serializer_class = CaseNotesHistorySerializerBase
    queryset = CaseNotesHistory.objects.all()
    model = CaseNotesHistory

    @property
    def pagination_class(self):
        """
        If with_extra query param is provided, the endpoint will return
        n+1 elements so that the frontend can build the diff from the
        current+prev element.
        """
        if self.request.query_params.get("with_extra", False):
            return PaginatorWithExtraItem
        return CaseNotesHistoryResultsSetPagination

    def get_queryset(self, **kwargs):
        qs = super(BaseCaseNotesHistoryViewSet, self).get_queryset(**kwargs)
        type_param = self.request.query_params.get("type", None)
        summary = self.request.query_params.get("summary", False)

        if type_param == "operator":
            qs = qs.filter(provider_notes__isnull=True)
        elif type_param == "cla_provider":
            qs = qs.filter(operator_notes__isnull=True)

        if summary == "true":
            qs = qs.filter(include_in_summary=True)
        return qs
