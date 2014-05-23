from django.contrib.auth.models import AnonymousUser

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import OrderingFilter, SearchFilter

from cla_common.constants import CASE_STATES
from cla_provider.models import Provider, OutOfHoursRota
from cla_provider.helpers import ProviderAllocationHelper
from core.viewsets import IsEligibleActionViewSetMixin
from legalaid.models import Category, EligibilityCheck, Case, CaseLogType
from legalaid.views import BaseUserViewSet

from .permissions import CallCentreClientIDPermission
from .serializers import EligibilityCheckSerializer, CategorySerializer, \
    CaseSerializer, ProviderSerializer, CaseLogSerializer, \
    OutOfHoursRotaSerializer, OperatorSerializer
from .forms import ProviderAllocationForm, CloseCaseForm
from .models import Operator


class CallCentrePermissionsViewSetMixin(object):
    permission_classes = (CallCentreClientIDPermission,)


class CategoryViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer

    lookup_field = 'code'


class CaseLogTypeViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = CaseLogType
    serializer_class = CaseLogSerializer

    lookup_field = 'code'


class EligibilityCheckViewSet(
    CallCentrePermissionsViewSetMixin,
    IsEligibleActionViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    model = EligibilityCheck
    serializer_class = EligibilityCheckSerializer

    lookup_field = 'reference'


class CaseViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Case.objects.filter(state=CASE_STATES.OPEN, provider=None)
    model = Case
    lookup_field = 'reference'
    serializer_class = CaseSerializer

    filter_backends = (
        OrderingFilter,
        SearchFilter,
    )

    ordering_fields = ('modified', 'created')
    ordering = '-modified'

    search_fields = ('personal_details__full_name',
                     'personal_details__postcode',
                     'reference')

    default_state_filter = [CASE_STATES.OPEN]
    all_states = dict(CASE_STATES.CHOICES).keys()

    def pre_save(self, obj, *args, **kwargs):
        super(CaseViewSet, self).pre_save(obj, *args, **kwargs)

        user = self.request.user
        if not obj.pk and not isinstance(user, AnonymousUser):
            obj.created_by = user

    @action()
    def assign(self, request, reference=None, **kwargs):
        """
        Assigns the case to a provider
        """
        obj = self.get_object()

        helper = ProviderAllocationHelper()
        category = obj.eligibility_check.category
        # Randomly assign to provider who offers this category of service
        form = ProviderAllocationForm({'provider' : helper.get_random_provider(category)},
                                      providers=helper.get_qualifying_providers(category))
        if form.is_valid():
            provider = form.save(obj, request.user)
            provider_serialised = ProviderSerializer(provider)
            return DRFResponse(data=provider_serialised.data)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )

    @action()
    def close(self, request, reference=None, **kwargs):
        """
        Closes a case
        """
        obj = self.get_object()
        form = CloseCaseForm(request.DATA)
        if form.is_valid():
            form.save(obj, request.user)
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )


class ProviderViewSet(CallCentrePermissionsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Provider
    serializer_class = ProviderSerializer

    queryset = Provider.objects.active()

class OutOfHoursRotaViewSet(
    CallCentrePermissionsViewSetMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet):

    serializer_class = OutOfHoursRotaSerializer
    model = OutOfHoursRota

class UserViewSet(CallCentrePermissionsViewSetMixin, BaseUserViewSet):
    model = Operator
    serializer_class = OperatorSerializer

    def get_logged_in_user_model(self):
        return self.request.user.operator
