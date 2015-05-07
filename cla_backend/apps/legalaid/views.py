import json
from core.drf.exceptions import ConflictException

from django import forms
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator

from django_statsd.clients import statsd

from legalaid.permissions import IsManagerOrMePermission
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, link
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import OrderingFilter, SearchFilter, \
    DjangoFilterBackend
from rest_framework_extensions.mixins import DetailSerializerMixin

from core.utils import format_patch
from core.drf.mixins import NestedGenericModelMixin, JsonPatchViewSetMixin, \
    FormActionMixin
from core.drf.pagination import RelativeUrlPaginationSerializer

from legalaid.permissions import IsManagerOrMePermission
from cla_eventlog import event_registry

from cla_auth.models import AccessAttempt

from .serializers import CategorySerializerBase, \
    MatterTypeSerializerBase, MediaCodeSerializerBase, \
    PersonalDetailsSerializerFull, ThirdPartyDetailsSerializerBase, \
    AdaptationDetailsSerializerBase, CaseSerializerBase, \
    FeedbackSerializerBase, CaseNotesHistorySerializerBase, \
    CSVUploadSerializerBase
from cla_provider.models import Feedback, CSVUpload
from .models import Case, Category, EligibilityCheck, \
    MatterType, MediaCode, PersonalDetails, ThirdPartyDetails, \
    AdaptationDetails, CaseNotesHistory


class CaseFormActionMixin(FormActionMixin):
    """
    This is for backward compatibility
    """
    FORM_ACTION_OBJ_PARAM = 'case'


class PasswordResetForm(forms.Form):

    new_password = forms.CharField(required=True, min_length=10)
    old_password = forms.CharField(required=False)

    def __init__(self, case=None, *args, **kwargs):
        self.action_user = kwargs.pop('action_user')
        self.reset_user = kwargs.pop('reset_user')

        super(PasswordResetForm, self).__init__(*args, **kwargs)

        if self.action_user == self.reset_user:
            self.fields['old_password'].required = True

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if self.action_user == self.reset_user:
            # changing own password
            if not self.reset_user.check_password(old_password):
                raise PermissionDenied({'__all__':["Old password doesn't match."]})
        return old_password


    def save(self, _):
        new_password = self.cleaned_data['new_password']
        self.reset_user.set_password(new_password)
        self.reset_user.save()


class BaseUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    CaseFormActionMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsManagerOrMePermission,)

    me_lookup_url_kwargs = 'me'
    lookup_field = 'user__username'

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
        logged_in_user_model = self.get_logged_in_user_model()

        if lookup == self.me_lookup_url_kwargs:
            self.kwargs[lookup_url_kwarg] = self.request.user.username

        obj =  super(BaseUserViewSet, self).get_object(*args, **kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    @action()
    def password_reset(self, request, *args, **kwargs):
        user = self.get_object().user
        try:
            return self._form_action(request, PasswordResetForm, no_body=True, form_kwargs={'action_user': request.user, 'reset_user': user})
        except PermissionDenied as pd:
            return DRFResponse(pd.detail, status=status.HTTP_403_FORBIDDEN)

    @action()
    def reset_lockout(self, request, *args, **kwargs):
        logged_in_user_model = self.get_logged_in_user_model()
        if not logged_in_user_model.is_manager:
            raise PermissionDenied()

        user = self.get_object().user
        AccessAttempt.objects.delete_for_username(user.username)
        statsd.incr('account.lockout.reset')
        return DRFResponse(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        if not self.get_logged_in_user_model().is_manager:
            raise PermissionDenied()
        return super(BaseUserViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        obj = super(BaseUserViewSet, self).create(request, *args, **kwargs)
        self.check_object_permissions(request, obj)
        return obj


class BaseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializerBase

    lookup_field = 'code'


class BaseEligibilityCheckViewSet(JsonPatchViewSetMixin, viewsets.GenericViewSet):
    model = EligibilityCheck
    lookup_field = 'reference'

    @link()
    def validate(self, request, **kwargs):
        obj = self.get_object()
        return DRFResponse(obj.validate())

    @action()
    def is_eligible(self, request, *args, **kwargs):
        obj = self.get_object()

        response, ec, reasons = obj.get_eligibility_state()
        return DRFResponse({
            'is_eligible': response
        })

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

        means_test_event = event_registry.get_event('means_test')()
        status = 'changed' if not created else 'created'
        kwargs = {
            'created_by': user,
            'status': status,
            'context': {'state': obj.state}
        }
        kwargs = self.get_means_test_event_kwargs(kwargs)
        means_test_event.process(obj.case, **kwargs)

    def post_save(self, obj, created=False, **kwargs):
        super(BaseEligibilityCheckViewSet, self).post_save(obj, created=created)

        self.create_means_test_log(obj, created=created)

        return obj


class BaseNestedEligibilityCheckViewSet(
        NestedGenericModelMixin, BaseEligibilityCheckViewSet
    ):

    PARENT_FIELD = 'eligibility_check'

    def get_means_test_event_kwargs(self, kwargs):
        patch = self.jsonpatch

        kwargs.update({
            'patch': json.dumps(patch),
            'notes': format_patch(patch['forwards']),
        })
        return kwargs


class BaseMatterTypeViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = MatterType
    serializer_class = MatterTypeSerializerBase

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('level', 'category__code')


class BaseMediaCodeViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = MediaCode
    serializer_class = MediaCodeSerializerBase

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name', 'group__name')


class FullPersonalDetailsViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet
):
    model = PersonalDetails
    serializer_class = PersonalDetailsSerializerFull
    lookup_field = 'reference'

    PARENT_FIELD = 'personal_details'


class BaseThirdPartyDetailsViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet
):
    model = ThirdPartyDetails
    serializer_class = ThirdPartyDetailsSerializerBase
    lookup_field = 'reference'
    PARENT_FIELD = 'thirdparty_details'


class BaseAdaptationDetailsViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    NestedGenericModelMixin,
    viewsets.GenericViewSet
):
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializerBase
    lookup_field = 'reference'
    PARENT_FIELD = 'adaptation_details'


class BaseAdaptationDetailsMetadataViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializerBase

    def create(self, request, *args, **kwargs):
        self.http_method_not_allowed(request)


class BaseCaseOrderingFilter(OrderingFilter):
    default_modified = 'modified'

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request)
        if not ordering:
            ordering = self.get_default_ordering(view)

        if isinstance(ordering, basestring):
            if ',' in ordering:
                ordering = ordering.split(',')
            else:
                ordering = [ordering]

        if 'requires_action_at' not in ordering:
            ordering.append('requires_action_at')

        if 'modified' not in ordering:
            ordering.append(self.default_modified)

        ordering = self.remove_invalid_fields(queryset, ordering, view)

        return queryset.order_by(*ordering)


class AscCaseOrderingFilter(BaseCaseOrderingFilter):
    default_modified = 'modified'


class DescCaseOrderingFilter(BaseCaseOrderingFilter):
    default_modified = '-modified'


class BaseCaseLogMixin(object):

    def get_log_notes(self, obj):
        raise NotImplementedError()

    def get_log_context(self, obj):
        context = {}
        if obj.eligibility_check:
            context['eligibility_state'] = obj.eligibility_check.state
        return context

    def post_save(self, obj, created=False):
        super(BaseCaseLogMixin, self).post_save(obj, created=created)

        if created:
            event = event_registry.get_event('case')()
            event.process(
                obj, status='created',
                created_by=obj.created_by,
                notes=self.get_log_notes(obj),
                context=self.get_log_context(obj)
            )

class FullCaseViewSet(
    DetailSerializerMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    CaseFormActionMixin,
    viewsets.GenericViewSet
):
    model = Case
    lookup_field = 'reference'
    lookup_regex = r'[A-Z|\d]{2}-\d{4}-\d{4}'

    serializer_class = CaseSerializerBase
    pagination_serializer_class = RelativeUrlPaginationSerializer

    filter_backends = (
        AscCaseOrderingFilter,
        SearchFilter,
    )

    ordering_fields = (
        'modified', 'personal_details__full_name', 'requires_action_at',
        'personal_details__date_of_birth', 'personal_details__postcode',
        'eligibility_check__category__name', 'priority', 'null_priority'
    )
    ordering = ['-priority']

    search_fields = (
        'personal_details__full_name',
        'personal_details__postcode',
        'personal_details__street',
        'personal_details__search_field',
        'reference',
        'laa_reference',
        'search_field'
    )
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    def get_queryset(self, **kwargs):
        qs = super(FullCaseViewSet, self).get_queryset(**kwargs)
        person_ref_param = self.request.QUERY_PARAMS.get('person_ref', None)
        dashboard_param = self.request.QUERY_PARAMS.get('dashboard', None)
        ordering = self.request.QUERY_PARAMS.get('ordering', None)

        if person_ref_param:
            qs = qs.filter(personal_details__reference=person_ref_param)
        elif dashboard_param:
            qs = self.get_dashboard_qs(qs)
        qs = qs.extra(
            select={
                'null_priority': '''CASE
                    WHEN legalaid_case.outcome_code IS NULL THEN 1
                    ELSE 0
                END''',
                'priority': '''CASE legalaid_case.outcome_code
                        WHEN 'REF-EXT' THEN 8
                        WHEN 'IRCB' THEN 7
                        WHEN 'MIS' THEN 6
                        WHEN 'COI' THEN 5
                        WHEN 'CB1' THEN 4
                        WHEN 'CB2' THEN 3
                        WHEN 'CB3' THEN 2
                        ELSE 1
                    END''',
                'rejected': '''CASE
                    WHEN legalaid_case.outcome_code IN (
                        'COI', 'MIS')
                    THEN 1
                    ELSE 0
                END'''})

        return qs

    def get_dashboard_qs(self, qs):
        return qs

    def retrieve(self, request, *args, **kwargs):
        resp = super(FullCaseViewSet, self).retrieve(request, *args, **kwargs)

        event = event_registry.get_event('case')()
        event.process(
            self.object, status='viewed', created_by=request.user,
            notes='Case viewed'
        )

        return resp

    def pre_save(self, obj):
        super(FullCaseViewSet, self).pre_save(obj)
        if obj.pk:
            if 'notes' in obj.changed_fields:
                cnh = CaseNotesHistory(case=obj)
                cnh.operator_notes = obj.notes
                cnh.created_by = self.request.user
                cnh.save()

            if 'provider_notes' in obj.changed_fields:
                cpnh = CaseNotesHistory(case=obj)
                cpnh.provider_notes = obj.provider_notes
                cpnh.created_by = self.request.user
                cpnh.save()

            if 'complaint_flag' in obj.changed_fields:
                event = event_registry.get_event('case')()
                event.process(
                    obj,
                    status='complaint_flag_toggled',
                    created_by=self.request.user,
                    notes='Complaint flag toggled: %s' % obj.complaint_flag
                )

            # if we want to add more checks on changed fields then we should
            # probably refactor this method to look at a list on the view
            # called 'action_on_changed_fields' and enumerate that and perform
            # the appropriate thing instead of adding more stuff here



class BaseFeedbackViewSet(
    NestedGenericModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = Feedback
    serializer_class = FeedbackSerializerBase
    PARENT_FIELD = 'provider_feedback'
    lookup_field = 'reference'


class BaseCSVUploadReadOnlyViewSet(
    DetailSerializerMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = CSVUpload

    serializer_class = CSVUploadSerializerBase
    serializer_detail_class = CSVUploadSerializerBase

    filter_backends = (
        OrderingFilter,
    )

class BaseCSVUploadViewSet(
    DetailSerializerMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = CSVUpload
    serializer_class = CSVUploadSerializerBase
    serializer_detail_class = CSVUploadSerializerBase

    filter_backends = (
        OrderingFilter,
    )

    def create(self, request, *args, **kwargs):
        try:
            return super(BaseCSVUploadViewSet, self).create(request, *args, **kwargs)
        except IntegrityError as ie:
            raise ConflictException("Upload already exists for given month. Try overwriting.")

    def update(self, request, *args, **kwargs):
        if request.method.upper() == u'PATCH':
            # Don't allow PATCH because they should DELETE+POST or PUT
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super(BaseCSVUploadViewSet, self).update(request, *args, **kwargs)

class PaginatorWithExtraItem(Paginator):
    """
    Same as the Paginator but it will return one more item than expected.
    Used for endpoints that need to diff elements.
    """
    extra_num = 1

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + (self.per_page + self.extra_num)
        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(self.object_list[bottom:top], number, self)


class BaseCaseNotesHistoryViewSet(
    NestedGenericModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    PARENT_FIELD = 'casenoteshistory_set'
    lookup_field = 'reference'
    serializer_class = CaseNotesHistorySerializerBase
    model = CaseNotesHistory

    pagination_serializer_class = RelativeUrlPaginationSerializer
    paginate_by = 5
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    @property
    def paginator_class(self):
        """
        If with_extra query param is provided, the endpoint will return
        n+1 elements so that the frontend can build the diff from the
        current+prev element.
        """
        if self.request.QUERY_PARAMS.get('with_extra', False):
            return PaginatorWithExtraItem
        return Paginator

    def get_queryset(self, **kwargs):
        qs = super(BaseCaseNotesHistoryViewSet, self).get_queryset(**kwargs)
        type_param = self.request.QUERY_PARAMS.get('type', None)
        summary = self.request.QUERY_PARAMS.get('summary', False)

        if type_param == 'operator':
            qs = qs.filter(provider_notes__isnull=True)
        elif type_param == 'cla_provider':
            qs = qs.filter(operator_notes__isnull=True)

        if summary == 'true':
            qs = qs.filter(include_in_summary=True)
        return qs
