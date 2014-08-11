import json

from django.http import Http404

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, link
from rest_framework.response import Response as DRFResponse
from rest_framework.filters import DjangoFilterBackend

from core.utils import format_patch
from core.drf.mixins import NestedGenericModelMixin, JsonPatchViewSetMixin

from cla_eventlog import event_registry

from .serializers import CategorySerializerBase, \
    MatterTypeSerializerBase, MediaCodeSerializerBase
from .models import Case, Category, EligibilityCheck, \
    MatterType, MediaCode


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


class FormActionMixin(object):
    def _form_action(self, request, Form):
        obj = self.get_object()
        form = Form(case=obj, data=request.DATA)
        if form.is_valid():
            form.save(request.user)
            return DRFResponse(status=status.HTTP_204_NO_CONTENT)

        return DRFResponse(
            dict(form.errors), status=status.HTTP_400_BAD_REQUEST
        )


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

        response = obj.get_eligibility_state()
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
