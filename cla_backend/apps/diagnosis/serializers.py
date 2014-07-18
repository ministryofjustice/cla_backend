from core.serializers import ClaModelSerializer
from diagnosis.models import DiagnosisTraversal
from rest_framework.fields import ChoiceField, SerializerMethodField, \
    WritableField

from core.serializers import JSONField

from .graph import graph


class DiagnosisSerializer(ClaModelSerializer):
    choices = SerializerMethodField('get_choices')
    nodes = JSONField(read_only=True)
    current_node_id = ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(DiagnosisSerializer, self).__init__(*args, **kwargs)
        self.graph = graph

        choices = self._get_choices()
        self.fields['current_node_id'].choices = choices
        self.fields['current_node_id'].required = bool(choices)

    def get_choices(self, request):
        choices = self._get_choices()

        choice_list = []
        for choice_tuple in choices:
            choice_list.append({
                'id': choice_tuple[0],
                'label': choice_tuple[1]
            })
        return choice_list

    def _get_choices(self, request=None):
        if not self.object:
            return []
        # if not hasattr(self, '_get_choices'):
        current_node_id = self.object.current_node_id
        if not current_node_id:
            current_node_id = 'root'

        # populating choices
        children = self.graph.successors(current_node_id)
        return [(node_id, self.graph.node[node_id]['label']) for node_id in children]

        # return self._get_choices

    def save_object(self, obj, **kwargs):
        if obj.current_node_id:
            current_node = self.graph.node[obj.current_node_id]

            nodes = obj.nodes or []
            nodes.append(current_node)
            obj.nodes = nodes

        return super(DiagnosisSerializer, self).save_object(obj, **kwargs)

    class Meta:
        model = DiagnosisTraversal
        fields = ('nodes', 'choices', 'current_node_id')
