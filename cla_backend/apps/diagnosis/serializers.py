from core.serializers import ClaModelSerializer
from diagnosis.models import DiagnosisTraversal
from rest_framework.fields import ChoiceField, SerializerMethodField, \
    WritableField
from rest_framework.serializers import Serializer


class MoveSerializer(Serializer):
    answer = ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        super(MoveSerializer, self).__init__(*args, **kwargs)
        self.fields['answer'].choices = choices

class DiagnosisSerializer(ClaModelSerializer):


    choices = SerializerMethodField('get_choices')
    current_node = ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(DiagnosisSerializer, self).__init__(*args, **kwargs)
        self.fields['current_node'].choices = self.get_choices()

    def get_choices(self, request=None):
        return []

    class Meta:
        model = DiagnosisTraversal
        fields = ('nodes','choices','current_node')

