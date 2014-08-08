import json
from call_centre.utils import format_patch
from cla_eventlog import event_registry
from core.drf.mixins import NestedGenericModelMixin
from dateutil import parser
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
import jsonpatch

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, link
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import OrderingFilter, SearchFilter, \
    DjangoFilterBackend

from cla_provider.models import Provider, OutOfHoursRota
from cla_provider.helpers import ProviderAllocationHelper
from cla_eventlog.views import BaseEventViewSet
from timer.views import BaseTimerViewSet
from legalaid.models import Case, PersonalDetails, ThirdPartyDetails, \
    AdaptationDetails, MatterType, MediaCode
from legalaid.views import BaseUserViewSet, FormActionMixin, \
    BaseCategoryViewSet, BaseEligibilityCheckViewSet
from cla_common.constants import REQUIRES_ACTION_BY
from knowledgebase.views import BaseArticleViewSet, BaseArticleCategoryViewSet
from diagnosis.views import BaseDiagnosisViewSet

from .permissions import CallCentreClientIDPermission, \
    OperatorManagerPermission
from .serializers import EligibilityCheckSerializer, \
    CaseSerializer, ProviderSerializer,  \
    OutOfHoursRotaSerializer, OperatorSerializer, PersonalDetailsSerializer, \
    ThirdPartyDetailsSerializer, AdaptationDetailsSerializer, \
    MatterTypeSerializer, MediaCodeSerializer

from .forms import ProviderAllocationForm,  DeclineHelpCaseForm,\
    DeferAssignmentCaseForm, SuspendCaseForm, AlternativeHelpForm

from .models import Operator


class CallCentrePermissionsViewSetMixin(object):
    permission_classes = (CallCentreClientIDPermission,)


class CallCentreManagerPermissionsViewSetMixin(object):
    permission_classes = (
        CallCentreClientIDPermission, OperatorManagerPermission)


class CategoryViewSet(CallCentrePermissionsViewSetMixin, BaseCategoryViewSet):
    pass


class EligibilityCheckViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    NestedGenericModelMixin,
    BaseEligibilityCheckViewSet,
):
    serializer_class = EligibilityCheckSerializer
    PARENT_FIELD = 'eligibility_check'


    @link()
    def validate(self, request, **kwargs):
        obj = self.get_object()
        return DRFResponse(obj.validate())

    @property
    def jsonpatch(self):
        forwards = jsonpatch.JsonPatch.from_diff(self.__pre_save__, self.__post_save__)
        backwards = jsonpatch.JsonPatch.from_diff(self.__post_save__, self.__pre_save__)
        serializer = self.get_serializer_class()

        return {
            'serializer': '.'.join([serializer.__module__, serializer.__name__]),
            'backwards': backwards.patch,
            'forwards': forwards.patch
        }

    def pre_save(self, obj):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data

    def post_save(self, obj, created=False, **kwargs):
        super(EligibilityCheckViewSet, self).post_save(obj, created=created)
        user = self.request.user
        self.__post_save__ = self.get_serializer_class()(obj).data

        patch = self.jsonpatch

        means_test_event = event_registry.get_event('means_test')()
        status = 'changed' if not created else 'created'
        means_test_event.process(obj.case,
                                 patch=json.dumps(patch),
                                 notes=format_patch(patch['forwards']),
                                 created_by=user,
                                 status=status
        )

        return obj

class MatterTypeViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = MatterType
    serializer_class = MatterTypeSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('level', 'category__code')


class MediaCodeViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    model = MediaCode
    serializer_class = MediaCodeSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name', 'group__name')


class CaseViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    FormActionMixin,
    viewsets.GenericViewSet
):
    model = Case
    lookup_field = 'reference'
    lookup_regex = r'[A-Z|\d]{2}-\d{4}-\d{4}'

    serializer_class = CaseSerializer

    filter_backends = (
        OrderingFilter,
        SearchFilter,
    )

    ordering_fields = ('modified', 'created')
    ordering = '-modified'

    search_fields = ('personal_details__full_name',
                     'personal_details__postcode',
                     'reference',
                     'laa_reference')
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100


    def get_queryset(self):
        qs = super(CaseViewSet, self).get_queryset()
        dashboard_param = self.request.QUERY_PARAMS.get('dashboard', None)
        if dashboard_param:
            qs = qs.filter(requires_action_by=REQUIRES_ACTION_BY.OPERATOR)
        return qs

    def pre_save(self, obj, *args, **kwargs):
        super(CaseViewSet, self).pre_save(obj, *args, **kwargs)

        user = self.request.user
        if not obj.pk and not isinstance(user, AnonymousUser):
            obj.created_by = user

    @link()
    def assign_suggest(self, request, reference=None, **kwargs):
        """
        @return: dict - 'suggested_provider' (single item) ;
                        'suitable_providers' all possible providers for this category.
        """

        as_of = None
        if 'as_of' in request.GET and (settings.DEBUG or settings.TEST_MODE):
            as_of = parser.parse(request.GET.get('as_of'))
            as_of = as_of.replace(tzinfo=timezone.get_current_timezone())

        obj = self.get_object()
        helper = ProviderAllocationHelper(as_of=as_of)

        if hasattr(obj, 'eligibility_check') and obj.eligibility_check != None and obj.eligibility_check.category:
            category = obj.eligibility_check.category
            suggested = helper.get_suggested_provider(category)

            if suggested:
                suggested_provider = ProviderSerializer(suggested).data
            else:
                suggested_provider = None
        else:
            category = None
            suggested_provider = None

        suitable_providers = [
            ProviderSerializer(p).data for p in helper.get_qualifying_providers(category)]
        suggestions = {'suggested_provider': suggested_provider,
                       'suitable_providers': suitable_providers,
                       'as_of': helper.as_of
                       }

        return DRFResponse(suggestions)

    @action()
    def assign(self, request, reference=None, **kwargs):
        """
        Assigns the case to a provider
        """
        obj = self.get_object()
        helper = ProviderAllocationHelper()

        category = obj.eligibility_check.category if obj.eligibility_check else None
        suitable_providers = helper.get_qualifying_providers(category)

        # find given provider in suitable - avoid extra lookup and ensures
        # valid provider
        for sp in suitable_providers:
            if sp.id == int(request.DATA['provider_id']):
                p = sp
                break
        else:
            raise ValueError("Provider not found")

        # if we're inside office hours then:
        # Randomly assign to provider who offers this category of service
        # else it should be the on duty provider
        data = request.DATA.copy()
        data['provider'] = p.pk
        form = ProviderAllocationForm(case=obj,
                                      data=data,
                                      providers=suitable_providers)

        if form.is_valid():
            provider = form.save(request.user)
            provider_serialised = ProviderSerializer(provider)
            return DRFResponse(data=provider_serialised.data)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )

    @action()
    def defer_assignment(self, request, **kwargs):
        obj = self.get_object()
        form = DeferAssignmentCaseForm(case=obj, data=request.DATA)
        if form.is_valid():
            form.save(request.user)
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )

    @action()
    def decline_help(self, request, reference=None, **kwargs):
        return self._form_action(request, DeclineHelpCaseForm)

    @action()
    def suspend(self, request, reference=None, **kwargs):
        return self._form_action(request, SuspendCaseForm)

    def retrieve(self, request, *args, **kwargs):
        resp = super(CaseViewSet, self).retrieve(request, *args, **kwargs)

        event = event_registry.get_event('case')()
        event.process(
            self.object, status='viewed', created_by=request.user,
            notes='Case viewed'
        )

        return resp

    @action()
    def assign_alternative_help(self, request, **kwargs):
        return self._form_action(request, AlternativeHelpForm)

    def post_save(self, obj, created=False):
        super(CaseViewSet, self).post_save(obj, created=created)

        if created:
            event = event_registry.get_event('case')()
            event.process(
                obj, status='created', created_by=self.request.user,
                notes="Case created"
            )


class ProviderViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Provider
    serializer_class = ProviderSerializer

    queryset = Provider.objects.active()

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('law_category__code',)


class OutOfHoursRotaViewSet(
    CallCentreManagerPermissionsViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    serializer_class = OutOfHoursRotaSerializer
    model = OutOfHoursRota


class UserViewSet(CallCentrePermissionsViewSetMixin, BaseUserViewSet):
    model = Operator
    serializer_class = OperatorSerializer

    def get_logged_in_user_model(self):
        return self.request.user.operator


class PersonalDetailsViewSet(CallCentrePermissionsViewSetMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.RetrieveModelMixin,
                             NestedGenericModelMixin,
                             viewsets.GenericViewSet):
    model = PersonalDetails
    serializer_class = PersonalDetailsSerializer
    lookup_field = 'reference'

    PARENT_FIELD = 'personal_details'

class EventViewSet(CallCentrePermissionsViewSetMixin, BaseEventViewSet):
    pass


class ThirdPartyDetailsViewSet(CallCentrePermissionsViewSetMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.RetrieveModelMixin,
                             NestedGenericModelMixin,
                             viewsets.GenericViewSet):
    model = ThirdPartyDetails
    serializer_class = ThirdPartyDetailsSerializer
    lookup_field = 'reference'
    PARENT_FIELD = 'thirdparty_details'


class AdaptationDetailsViewSet(CallCentrePermissionsViewSetMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.RetrieveModelMixin,
                             NestedGenericModelMixin,
                             viewsets.GenericViewSet):
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializer
    lookup_field = 'reference'
    PARENT_FIELD = 'adaptation_details'


class AdaptationDetailsMetadataViewSet(CallCentrePermissionsViewSetMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet):
    model = AdaptationDetails
    serializer_class = AdaptationDetailsSerializer

    def create(self, request, *args, **kwargs):
        self.http_method_not_allowed(request)


class ArticleViewSet(CallCentrePermissionsViewSetMixin, BaseArticleViewSet):
    pass


class ArticleCategoryViewSet(CallCentrePermissionsViewSetMixin,
                             BaseArticleCategoryViewSet):
    pass


class TimerViewSet(CallCentrePermissionsViewSetMixin, BaseTimerViewSet):
    pass


class DiagnosisViewSet(CallCentrePermissionsViewSetMixin, BaseDiagnosisViewSet):
    pass
