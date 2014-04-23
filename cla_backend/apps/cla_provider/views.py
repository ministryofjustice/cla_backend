from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse

from core.viewsets import DefaultStateFilterViewSetMixin, \
    IsEligibleActionViewSetMixin
from cla_common.constants import CASE_STATE_OPEN, CASE_STATE_CHOICES

from legalaid.exceptions import InvalidMutationException
from legalaid.models import Category, EligibilityCheck, Case, OutcomeCode

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from .serializers import CategorySerializer, \
    EligibilityCheckSerializer, CaseSerializer, OutcomeCodeSerializer
from .forms import RejectCaseForm, AcceptCaseForm


class CLAProviderPermissionViewSetMixin(object):
    permission_classes = (CLAProviderClientIDPermission,)


class CategoryViewSet(CLAProviderPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

    lookup_field = 'code'


class OutcomeCodeViewSet(
    CLAProviderPermissionViewSetMixin,
    DefaultStateFilterViewSetMixin,
    viewsets.ReadOnlyModelViewSet
):
    model = OutcomeCode
    serializer_class = OutcomeCodeSerializer

    lookup_field = 'code'

    default_state_filter = None
    all_states = dict(CASE_STATE_CHOICES).keys()
    state_field = 'case_state'



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

    ordering_fields = ('modified', 'created')
    ordering = '-modified'

    default_state_filter = CASE_STATE_OPEN
    all_states = dict(CASE_STATE_CHOICES).keys()

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
