from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action

from core.viewsets import DefaultStateFilterViewSetMixin
from cla_common.constants import CASE_STATES
from legalaid.serializers import CaseLogTypeSerializerBase

from legalaid.models import Category, EligibilityCheck, Case, CaseLogType
from legalaid.views import BaseUserViewSet, StateFromActionMixin, \
    BaseOutcomeCodeViewSet, BaseEligibilityCheckViewSet

from .models import Staff
from .permissions import CLAProviderClientIDPermission
from .serializers import CategorySerializer, \
    EligibilityCheckSerializer, CaseSerializer, StaffSerializer
from .forms import RejectCaseForm, AcceptCaseForm, CloseCaseForm


class CLAProviderPermissionViewSetMixin(object):
    permission_classes = (CLAProviderClientIDPermission,)


class CategoryViewSet(CLAProviderPermissionViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

    lookup_field = 'code'


class CaseLogTypeViewSet(
    CLAProviderPermissionViewSetMixin,
    viewsets.ReadOnlyModelViewSet
):
    model = CaseLogType
    serializer_class = CaseLogTypeSerializerBase

    lookup_field = 'code'


class EligibilityCheckViewSet(
    CLAProviderPermissionViewSetMixin,
    mixins.RetrieveModelMixin,
    BaseEligibilityCheckViewSet
):
    serializer_class = EligibilityCheckSerializer


class OutcomeCodeViewSet(
    CLAProviderPermissionViewSetMixin, BaseOutcomeCodeViewSet
):
    pass


class CaseViewSet(
    CLAProviderPermissionViewSetMixin,
    DefaultStateFilterViewSetMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    StateFromActionMixin,
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


class UserViewSet(CLAProviderPermissionViewSetMixin, BaseUserViewSet):
    model = Staff
    serializer_class = StaffSerializer

    def get_queryset(self):
        this_provider = get_object_or_404(Staff, user=self.request.user).provider
        qs = super(UserViewSet, self).get_queryset().filter(provider=this_provider)
        return qs

    def get_logged_in_user_model(self):
        return self.request.user.staff
