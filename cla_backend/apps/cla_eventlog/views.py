from rest_framework import mixins, viewsets, views, status
from rest_framework.response import Response as DRFResponse

from core.drf.mixins import NestedGenericModelMixin

from cla_eventlog.constants import LOG_LEVELS
from cla_eventlog import event_registry

from .serializers import LogSerializerBase
from .models import Log


class BaseEventViewSet(viewsets.ViewSetMixin, views.APIView):
    """
    This ViewSet defines two endpoints:
        /event/<event_key>/ : returns a list of codes by event_key

        /event/selectable/  : returns a list of selectable codes

    This is not DRF standard but it's a good way to group the logic behind
    events using ViewSets.
    """

    lookup_field = "action"

    def retrieve(self, request, *args, **kwargs):
        action = kwargs.pop(self.lookup_field)

        if action == "selectable":
            return self.selectable(request, *args, **kwargs)

        return self.list_by_event_key(request, action, *args, **kwargs)

    def selectable(self, request, *args, **kwargs):
        # Not implemented as not needed at the moment
        raise NotImplementedError()

    def list_by_event_key(self, request, event_key, *args, **kwargs):
        try:
            event = event_registry.get_event(event_key)
        except ValueError:
            return DRFResponse({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        response_data = self.format_codes(event.get_ordered_codes())
        return DRFResponse(response_data, status=status.HTTP_200_OK)

    def format_codes(self, codes):
        return [{"code": code, "description": code_data["description"]} for code, code_data in codes.items()]


class BaseLogViewSet(NestedGenericModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    PARENT_FIELD = "log_set"
    lookup_field = "reference"
    serializer_class = LogSerializerBase
    model = Log

    def get_queryset(self):
        qs = super(BaseLogViewSet, self).get_queryset()
        return qs.filter(level__gt=LOG_LEVELS.MINOR)
