from django.core.exceptions import ImproperlyConfigured
from checker.helpers import notify_callback_created
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny
from rest_framework import viewsets, mixins

from core.models import get_web_user
from diagnosis.views import DiagnosisModelMixin

from knowledgebase.views import BaseArticleViewSet, \
    ArticleCategoryFilter

from legalaid.models import EligibilityCheck, Property, Case
from legalaid.views import BaseCategoryViewSet, BaseEligibilityCheckViewSet, \
    BaseCaseLogMixin, CaseFormActionMixin
from cla_common.constants import CASE_SOURCE

from .serializers import EligibilityCheckSerializer, \
    PropertySerializer, CaseSerializer, CheckerDiagnosisSerializer
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
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    CaseFormActionMixin,
    viewsets.GenericViewSet
):

    model = Case
    serializer_class = CaseSerializer

    lookup_field = 'reference'
    lookup_regex = r'[A-Z|\d]{2}-\d{4}-\d{4}'

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
