from core.serializers import ClaModelSerializer
from .models import Timer


class TimerSerializer(ClaModelSerializer):
    class Meta(object):
        model = Timer
        fields = ('created',)
