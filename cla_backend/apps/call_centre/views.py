from uuid import UUID
from dateutil import parser

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, link
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import OrderingFilter, DjangoFilterBackend, \
    SearchFilter, BaseFilterBackend

from cla_provider.models import Provider, OutOfHoursRota, Feedback
from cla_eventlog import event_registry
from cla_eventlog.views import BaseEventViewSet, BaseLogViewSet
from cla_provider.helpers import ProviderAllocationHelper, notify_case_assigned

from timer.views import BaseTimerViewSet

from legalaid.models import PersonalDetails
from legalaid.views import BaseUserViewSet, \
    BaseCategoryViewSet, BaseNestedEligibilityCheckViewSet, \
    BaseMatterTypeViewSet, BaseMediaCodeViewSet, FullPersonalDetailsViewSet, \
    BaseThirdPartyDetailsViewSet, BaseAdaptationDetailsViewSet, \
    BaseAdaptationDetailsMetadataViewSet, FullCaseViewSet, BaseFeedbackViewSet

from cla_common.constants import REQUIRES_ACTION_BY
from knowledgebase.views import BaseArticleViewSet, BaseArticleCategoryViewSet
from diagnosis.views import BaseDiagnosisViewSet

from .permissions import CallCentreClientIDPermission, \
    OperatorManagerPermission
from .serializers import EligibilityCheckSerializer, \
    CaseSerializer, ProviderSerializer,  \
    OutOfHoursRotaSerializer, OperatorSerializer, \
    AdaptationDetailsSerializer, PersonalDetailsSerializer, \
    BarePersonalDetailsSerializer, \
    ThirdPartyDetailsSerializer, LogSerializer, FeedbackSerializer, \
    CreateCaseSerializer

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
    BaseNestedEligibilityCheckViewSet,
):
    serializer_class = EligibilityCheckSerializer

    # this is to fix a stupid thing in DRF where pre_save doesn't call super
    def pre_save(self, obj):
        original_obj = self.get_object()
        self.__pre_save__ = self.get_serializer_class()(original_obj).data


class MatterTypeViewSet(
    CallCentrePermissionsViewSetMixin, BaseMatterTypeViewSet
):
    pass


class MediaCodeViewSet(
    CallCentrePermissionsViewSetMixin, BaseMediaCodeViewSet
):
    pass


class OrderingRejectedFirstFilter(OrderingFilter):

    def filter_queryset(self, request, qs, view):
        ordering = self.get_ordering(request)
        if ordering:
            ordering = self.remove_invalid_fields(qs, ordering, view)
        if not ordering:
            ordering = self.get_default_ordering(view)
        if not ordering:
            ordering = []

        dashboard_param = request.QUERY_PARAMS.get('dashboard', None)
        if dashboard_param:
            qs = qs.extra(select={
                'rejected': '''CASE
                        WHEN legalaid_case.outcome_code IN ('COI', 'MIS',
                            'MIS-OOS', 'MIS-MEAN') THEN 1
                        ELSE 0
                    END'''})
            qs = qs.order_by('-rejected', *ordering)

        elif ordering:
            qs = qs.order_by(*ordering)

        return qs

class DateRangeFilter(BaseFilterBackend):


    def filter_queryset(self, request, qs, view):

        filter = {}
        start_date = request.QUERY_PARAMS.get('start', None)
        end_date = request.QUERY_PARAMS.get('end', None)

        if start_date is not None:
            filter['{field}__gte'.format(field=view.date_range_field)] = parser.parse(start_date).replace(tzinfo=timezone.get_current_timezone())
        if end_date is not None:
            filter['{field}__lte'.format(field=view.date_range_field)] = parser.parse(end_date).replace(tzinfo=timezone.get_current_timezone())

        qs = qs.filter(**filter)
        return qs


class CaseViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.CreateModelMixin, FullCaseViewSet
):
    serializer_class = CaseSerializer  # using CreateCaseSerializer during creation

    filter_backends = (
        OrderingRejectedFirstFilter,
        SearchFilter,
    )

    def get_serializer_class(self):
        # if POST create request => use special Serializer
        #   otherwise use standard one
        if self.request.method == 'POST' and not self.kwargs.get('reference'):
            return CreateCaseSerializer
        return super(CaseViewSet, self).get_serializer_class()

    def get_dashboard_qs(self, qs):
        return qs.filter(requires_action_by=REQUIRES_ACTION_BY.OPERATOR)

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
            notify_case_assigned(provider, form.case)
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

    @link()
    def search_for_personal_details(self, request, reference=None, **kwargs):
        """
            You can only call this endpoint if the case doesn't have any
            personal_details record attached.
            This is by design as it feels slighly more secure than allowing
            clients to use a dedicated endpoint that they can call whenever
            they want.

            If things change in the future, feel free to add a dedicated
            endpoint for this though.

            Should return just ('reference', 'full_name', 'postcode', 'dob')
            and should NOT include vulnerable users.
        """
        obj = self.get_object()
        if obj.personal_details:
            return DRFResponse(
                {'error': 'This case is already linked to a Person'},
                status=status.HTTP_400_BAD_REQUEST
            )

        person_q = request.QUERY_PARAMS.get('person_q', '') or ''
        if len(person_q) >= 3:
            users = PersonalDetails.objects.filter(
                full_name__icontains=person_q
            ).exclude(vulnerable_user=True)
        else:
            users = []
        data = [BarePersonalDetailsSerializer(user).data for user in users]

        return DRFResponse(data)

    @action()
    def link_personal_details(self, request, reference=None, **kwargs):
        """
            TODO: refactor everything!
                * if not DATA.personal_details => return 400
                * if obj.personal_details != None => return 400
                * if personal_details does not exist => return 400
        """
        def error_response(msg):
            return DRFResponse(
                {'error': msg}, status=status.HTTP_400_BAD_REQUEST
            )

        obj = self.get_object()

        # check PARAM exists
        pd_ref = request.DATA.get('personal_details', None)
        if not pd_ref:
            return error_response('Param "personal_details" required')

        # check that case doesn't have personal_details
        if obj.personal_details:
            return error_response('A person is already linked to this case')

        # check that personal details exists
        try:
            pd_ref = UUID(pd_ref, version=4)

            personal_details = PersonalDetails.objects.get(reference=pd_ref)
        except ValueError, PersonalDetails.DoesNotExist:
            return error_response('Person with reference "%s" not found' % pd_ref)

        # link personal details to case
        obj.personal_details = personal_details
        obj.save(update_fields=['personal_details', 'modified'])

        return DRFResponse(status=status.HTTP_204_NO_CONTENT)


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


class PersonalDetailsViewSet(
    CallCentrePermissionsViewSetMixin, FullPersonalDetailsViewSet
):
    serializer_class = PersonalDetailsSerializer


class ThirdPartyDetailsViewSet(
    CallCentrePermissionsViewSetMixin, BaseThirdPartyDetailsViewSet
):
    serializer_class = ThirdPartyDetailsSerializer


class AdaptationDetailsViewSet(
    CallCentrePermissionsViewSetMixin, BaseAdaptationDetailsViewSet
):
    serializer_class = AdaptationDetailsSerializer


class AdaptationDetailsMetadataViewSet(
    CallCentrePermissionsViewSetMixin,
    BaseAdaptationDetailsMetadataViewSet
):
    serializer_class = AdaptationDetailsSerializer


class EventViewSet(CallCentrePermissionsViewSetMixin, BaseEventViewSet):
    pass


class ArticleViewSet(CallCentrePermissionsViewSetMixin, BaseArticleViewSet):
    pass


class ArticleCategoryViewSet(CallCentrePermissionsViewSetMixin,
                             BaseArticleCategoryViewSet):
    pass


class TimerViewSet(CallCentrePermissionsViewSetMixin, BaseTimerViewSet):
    pass


class DiagnosisViewSet(CallCentrePermissionsViewSetMixin, BaseDiagnosisViewSet):
    pass


class LogViewSet(CallCentrePermissionsViewSetMixin, BaseLogViewSet):
    serializer_class = LogSerializer


class FeedbackViewSet(CallCentreManagerPermissionsViewSetMixin,
                      mixins.ListModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    model = Feedback
    lookup_field = 'reference'
    serializer_class = FeedbackSerializer

    filter_backends = (
        OrderingFilter,
        DateRangeFilter,
    )
    ordering = ('resolved', '-modified', '-created',)
    date_range_field = 'created'
