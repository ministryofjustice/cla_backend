from django_statsd.clients import statsd
from rest_framework import viewsets, views, status
from rest_framework.response import Response as DRFResponse

from .utils import get_timer, get_or_create_timer
from .serializers import TimerSerializer


class BaseTimerViewSet(viewsets.ViewSetMixin, views.APIView):
    """
    """
    serializer_class = TimerSerializer

    def get_serializer(self, obj):
        return self.serializer_class(obj).data

    def create(self, request, *args, **kwargs):
        return self.get_or_create(request, *args, **kwargs)

    def get_or_create(self, request, *args, **kwargs):
        try:
            timer, created = get_or_create_timer(request.user)
        except ValueError as e:
            return DRFResponse(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = self.get_serializer(timer)
        resp_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return DRFResponse(data, resp_status)

    def get(self, request, *args, **kwargs):
        timer = get_timer(request.user)

        if not timer:
            return DRFResponse(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = self.get_serializer(timer)
        return DRFResponse(data)

    def delete(self, request, *args, **kwargs):
        timer = get_timer(request.user)
        statsd.incr('timer.cancel')
        statsd.incr('timer.cancel.user.%s' % request.user.pk)

        if not timer:
            return DRFResponse(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        timer.stop(cancelled=True)

        return DRFResponse(status=status.HTTP_204_NO_CONTENT)
