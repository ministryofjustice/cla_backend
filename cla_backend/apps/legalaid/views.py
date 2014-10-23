import json

from cla_provider.models import Feedback
from django import forms
from django.db import transaction
from legalaid.permissions import IsManagerOrMePermission
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, link
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import OrderingFilter, SearchFilter, \
    DjangoFilterBackend

from core.utils import format_patch
from core.drf.mixins import NestedGenericModelMixin, JsonPatchViewSetMixin
from core.drf.pagination import RelativeUrlPaginationSerializer
from cla_eventlog import event_registry
from rest_framework_extensions.mixins import DetailSerializerMixin
from .serializers import CategorySerializerBase, \
    MatterTypeSerializerBase, MediaCodeSerializerBase, \
    PersonalDetailsSerializerFull, ThirdPartyDetailsSerializerBase, \
    AdaptationDetailsSerializerBase, CaseSerializerBase, FeedbackSerializerBase
from .models import Case, Category, EligibilityCheck, \
    MatterType, MediaCode, PersonalDetails, ThirdPartyDetails, \
    AdaptationDetails, CaseNotesHistory


class FormActionMixin(object):
    def _form_action(self, request, Form, no_body=True, form_kwargs={}):
        obj = self.get_object()
        form = Form(case=obj, data=request.DATA, **form_kwargs)
        if form.is_valid():
            form.save(request.user)

            if no_body:
                return DRFResponse(status=status.HTTP_204_NO_CONTENT)
            else:
                serializer = self.get_serializer(obj)
                return DRFResponse(serializer.data, status=status.HTTP_200_OK)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )


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
    FormActionMixin,
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

        response, ec = obj.get_eligibility_state()
        return DRFResponse({
            'is_eligible': response
        })

    def get_means_test_event_kwargs(self, kwargs):
        return kwargs

    def create_means_test_log(self, obj, created):
        try:
            obj.case
        except Case.DoesNotExist:
            return

        user = self.request.user

        means_test_event = event_registry.get_event('means_test')()
        status = 'changed' if not created else 'created'

        kwargs = {
            'created_by': user,
            'status': status
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


class FullCaseViewSet(
    DetailSerializerMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    FormActionMixin,
    viewsets.GenericViewSet
):
    model = Case
    lookup_field = 'reference'
    lookup_regex = r'[A-Z|\d]{2}-\d{4}-\d{4}'

    serializer_class = CaseSerializerBase
    pagination_serializer_class = RelativeUrlPaginationSerializer

    filter_backends = (
        OrderingFilter,
        SearchFilter,
    )

    ordering_fields = ('modified', 'personal_details__full_name',
            'personal_details__date_of_birth', 'personal_details__postcode',
            'eligibility_check__category__name', 'priority', 'null_priority')
    ordering = ('null_priority', '-priority', '-modified')

    search_fields = (
        'personal_details__full_name',
        'personal_details__postcode',
        'personal_details__street',
        'reference',
        'laa_reference'
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
                        'COI', 'MIS', 'MIS-OOS', 'MIS-MEAN')
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
