from rest_framework import viewsets, views, status
from rest_framework.response import Response as DRFResponse

from .utils import get_timer, create_timer
from .serializers import TimerSerializer


class BaseTimerViewSet(viewsets.ViewSetMixin, views.APIView):
    """
    """
    serializer_class = TimerSerializer

    def get_serializer(self, obj):
        return self.serializer_class(obj).data

    def create(self, request, *args, **kwargs):
        timer = get_timer(request)

        try:
            timer = create_timer(request)
        except ValueError as e:
            return DRFResponse(
                {'detail': e.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = self.get_serializer(timer)
        return DRFResponse(data, status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        timer = get_timer(request)

        if not timer:
            return DRFResponse(
                {'detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = self.get_serializer(timer)
        return DRFResponse(data)
