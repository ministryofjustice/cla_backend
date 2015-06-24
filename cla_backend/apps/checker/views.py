from django.core.exceptions import ImproperlyConfigured
from rest_framework.decorators import action
from checker.helpers import notify_callback_created
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny
from rest_framework import viewsets, mixins
from rest_framework.response import Response as DRFResponse

from core.models import get_web_user
from diagnosis.views import DiagnosisModelMixin

from knowledgebase.views import BaseArticleViewSet, \
    ArticleCategoryFilter

from legalaid.models import EligibilityCheck, Property, Case
from legalaid.views import BaseCategoryViewSet, BaseEligibilityCheckViewSet, \
    BaseCaseLogMixin
from cla_common.constants import CASE_SOURCE

from .models import ReasonForContacting
from .serializers import EligibilityCheckSerializer, \
    PropertySerializer, CaseSerializer, CheckerDiagnosisSerializer, \
    ReasonForContactingSerializer
from .forms import WebCallMeBackForm


class PublicAPIViewSetMixin(object):
    permission_classes = (AllowAny,)


class CategoryViewSet(PublicAPIViewSetMixin, BaseCategoryViewSet):
    """
    This returns a list of all valid categories in the system.
    """
    pass


class ArticleCategoryNameFilter(ArticleCategoryFilter):

    class Meta(ArticleCategoryFilter.Meta):
        fields = ('article_category__name',)


class ArticleViewSet(PublicAPIViewSetMixin, BaseArticleViewSet):
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    filter_class = ArticleCategoryNameFilter


class EligibilityCheckViewSet(
    PublicAPIViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    BaseEligibilityCheckViewSet
):
    serializer_class = EligibilityCheckSerializer

    def get_request_user(self):
        return get_web_user()

    @action()
    def is_eligible(self, request, *args, **kwargs):
        obj = self.get_object()

        response, ec, reasons = obj.get_eligibility_state()
        return DRFResponse({
            'is_eligible': response,
            'reasons': reasons
        })


class NestedModelMixin(object):

    parent_model = None
    parent_lookup = None
    nested_lookup = None

    @csrf_exempt
    def dispatch(self, request,  *args, **kwargs):
        key = kwargs['{parent_lookup}__{lookup}'. \
            format(parent_lookup=self.parent_lookup, lookup=self.nested_lookup)]

        self.parent_instance = get_object_or_404(
            self.parent_model, **{self.nested_lookup: key})

        return super(NestedModelMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(NestedModelMixin, self).get_queryset()
        return qs.filter(**{self.parent_lookup: self.parent_instance})

    def pre_save(self, obj):
        setattr(obj, self.parent_lookup, self.parent_instance)
        super(NestedModelMixin, self).pre_save(obj)


class PropertyViewSet(
    PublicAPIViewSetMixin,
    NestedModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):

    nested_lookup = 'reference'
    parent_lookup = 'eligibility_check'
    parent_model = EligibilityCheck

    model = Property
    serializer_class = PropertySerializer


class CaseViewSet(
    PublicAPIViewSetMixin,
    BaseCaseLogMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):

    model = Case
    serializer_class = CaseSerializer

    def pre_save(self, obj, *args, **kwargs):
        super(CaseViewSet, self).pre_save(obj, *args, **kwargs)

        if not obj.created_by:
            obj.created_by = get_web_user()
        obj.source = CASE_SOURCE.WEB

    def get_log_notes(self, obj):
        return "Case created digitally"

    def post_save(self, obj, created=False):
        super(CaseViewSet, self).post_save(obj, created=created)

        if created and obj.requires_action_at:
                form = WebCallMeBackForm(
                    case=obj, data={},
                    requires_action_at=obj.requires_action_at
                )

                if form.is_valid():
                    form.save(obj.created_by)
                    notify_callback_created(obj)


class DiagnosisViewSet(
    PublicAPIViewSetMixin,
    DiagnosisModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CheckerDiagnosisSerializer

    def get_current_user(self):
        return get_web_user()

    def pre_save(self, obj, *args, **kwargs):
        try:
            self._original_obj = self.get_object()
        except ImproperlyConfigured:
            pass
        return super(DiagnosisModelMixin, self).pre_save(obj, *args, **kwargs)


class ReasonForContactingViewSet(
    PublicAPIViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    model = ReasonForContacting
    serializer_class = ReasonForContactingSerializer
    lookup_field = 'reference'

    def pre_save(self, obj):
        # delete all existing reasons and use those from request as replacement set if provided
        if obj.pk and 'reasons' in self.request.DATA:
            obj.reasons.all().delete()

        super(ReasonForContactingViewSet, self).pre_save(obj)
