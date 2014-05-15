from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse

from core.viewsets import DefaultStateFilterViewSetMixin, \
    IsEligibleActionViewSetMixin
from cla_common.constants import CASE_STATES

from legalaid.exceptions import InvalidMutationException
from legalaid.models import Category, EligibilityCheck, Case, CaseLogType
from call_centre.serializers import CaseLogTypeSerializer

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from .serializers import CategorySerializer, \
    EligibilityCheckSerializer, CaseSerializer
from .forms import RejectCaseForm, AcceptCaseForm, CloseCaseForm
from legalaid.constants import CASELOGTYPE_SUBTYPES


class CLAProviderPermissionViewSetMixin(object):
    permission_classes = (CLAProviderClientIDPermission,)


class CategoryViewSet(CLAProviderPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

    lookup_field = 'code'


class CaseLogTypeViewSet(
    CLAProviderPermissionViewSetMixin,
    DefaultStateFilterViewSetMixin,
    viewsets.ReadOnlyModelViewSet
):
    model = CaseLogType
    serializer_class = CaseLogTypeSerializer

    lookup_field = 'code'

    default_state_filter = []
    all_states = dict(CASE_STATES.CHOICES).keys()
    state_field = 'case_state'


class OutcomeCodeViewSet(
    CLAProviderPermissionViewSetMixin,
    DefaultStateFilterViewSetMixin,
    viewsets.ReadOnlyModelViewSet
):
    model = CaseLogType
    serializer_class = CaseLogTypeSerializer

    lookup_field = 'code'

    default_state_filter = []
    all_states = dict(CASE_STATES.CHOICES).keys()
    state_field = 'case_state'

    queryset =  CaseLogType.objects.filter(subtype=CASELOGTYPE_SUBTYPES.OUTCOME)


class EligibilityCheckViewSet(
    CLAProviderPermissionViewSetMixin,
    IsEligibleActionViewSetMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = EligibilityCheck
    serializer_class = EligibilityCheckSerializer

    lookup_field = 'reference'


class CaseViewSet(
    CLAProviderPermissionViewSetMixin,
    DefaultStateFilterViewSetMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Case.objects.exclude(provider=None)
    model = Case
    lookup_field = 'reference'
    serializer_class = CaseSerializer

    filter_backends = (
        OrderingFilter,
        SearchFilter,
    )

    search_fields = ('personal_details__full_name',
                     'personal_details__postcode',
                     'reference' )

    ordering_fields = ('state', 'modified', 'created')
    ordering = ('-state', '-locked_by', '-modified', '-created')

    default_state_filter = [CASE_STATES.OPEN, CASE_STATES.ACCEPTED]
    all_states = dict(CASE_STATES.CHOICES).keys()

    def get_queryset(self):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(CaseViewSet, self).get_queryset().filter(provider=this_provider)
        return qs

    def get_object(self, *args, **kwargs):
        """
        Lock the object every time it's requested
        """
        obj = super(CaseViewSet, self).get_object(*args, **kwargs)
        if self.request:
            obj.lock(self.request.user)
        return obj

    def _state_form_action(self, request, Form):
        obj = self.get_object()
        form = Form(request.DATA)
        if form.is_valid():
            try:
                form.save(obj, request.user)
            except InvalidMutationException as e:
                return DRFResponse(
                    {'case_state': [unicode(e)]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )

    @action()
    def reject(self, request, reference=None, **kwargs):
        """
        Rejects a case
        """
        return self._state_form_action(request, Form=RejectCaseForm)

    @action()
    def accept(self, request, reference=None, **kwargs):
        """
        Accepts a case
        """
        return self._state_form_action(request, Form=AcceptCaseForm)

    @action()
    def close(self, request, reference=None, **kwargs):
        """
        Closes a case
        """
        return self._state_form_action(request, Form=CloseCaseForm)
