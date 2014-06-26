from django.http import Http404

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import DjangoFilterBackend

from legalaid.serializers import CaseLogTypeSerializerBase, CategorySerializerBase
from legalaid.constants import CASELOGTYPE_SUBTYPES
from legalaid.models import CaseLogType, Category, EligibilityCheck

from .exceptions import InvalidMutationException


class BaseUserViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):

    me_lookup_url_kwargs = 'me'

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
        if lookup != self.me_lookup_url_kwargs:
            raise Http404

        self.kwargs[lookup_url_kwarg] = self.get_logged_in_user_model().pk
        return super(BaseUserViewSet, self).get_object(*args, **kwargs)


class StateFromActionMixin(object):
    def _state_form_action(self, request, Form):
        obj = self.get_object()
        form = Form(case=obj, data=request.DATA)
        if form.is_valid():
            try:
                form.save(request.user)
            except InvalidMutationException as e:
                return DRFResponse(
                    {'case_state': [unicode(e)]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )


class BaseOutcomeCodeViewSet(
    viewsets.ReadOnlyModelViewSet
):
    model = CaseLogType
    serializer_class = CaseLogTypeSerializerBase

    lookup_field = 'code'

    queryset =  CaseLogType.objects.filter(subtype=CASELOGTYPE_SUBTYPES.OUTCOME)

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('action_key',)


class BaseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializerBase

    lookup_field = 'code'


class BaseEligibilityCheckViewSet(viewsets.GenericViewSet):
    model = EligibilityCheck
    lookup_field = 'reference'

    @action()
    def is_eligible(self, request, *args, **kwargs):
        obj = self.get_object()

        response = obj.get_eligibility_state()
        return DRFResponse({
            'is_eligible': response
        })
