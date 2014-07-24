from core.serializers import ClaModelSerializer
from diagnosis.models import DiagnosisTraversal
from rest_framework.fields import ChoiceField, SerializerMethodField
from cla_common.constants import DIAGNOSIS_SCOPE

from legalaid.models import Category

from .graph import graph
from rest_framework.relations import SlugRelatedField
from .utils import is_terminal


class DiagnosisSerializer(ClaModelSerializer):
    choices = SerializerMethodField('get_choices')
    nodes = SerializerMethodField('get_nodes')
    current_node_id = ChoiceField(choices=[])
    category = SlugRelatedField('category', slug_field='code', required=False)

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

    def get_nodes(self, request):
        if not self.object:
            return []

        nodes = self.object.nodes
        if nodes and is_terminal(self.graph, nodes[-1]['id']):
            nodes = nodes[:-1]

        return nodes

    def _get_choices(self, request=None):
        if not self.object:
            return []
        # if not hasattr(self, '_get_choices'):
        current_node_id = self.object.current_node_id
        if not current_node_id:
            current_node_id = self.graph.graph['operator_root_id']

        # populating choices
        children = self.graph.successors(current_node_id)
        nodes = [(node_id, self.graph.node[node_id]['label']) for node_id in children]
        nodes = sorted(nodes, key=lambda i: self.graph.node[i[0]]['order'])
        return nodes

    def get_context(self, obj):
        context = {}
        if obj.nodes:
            for node in obj.nodes:
                context.update(node['context'] or {})
        return context

    def _set_state(self, obj):
        if is_terminal(self.graph, obj.current_node_id):
            current_node = self.graph.node[obj.current_node_id]
            obj.state = DIAGNOSIS_SCOPE.CHOICES_CONST_DICT.get(current_node['label'], DIAGNOSIS_SCOPE.UNKNOWN)

            category_name = self.get_context(obj).get('category')
            if category_name:
                try:
                    category = Category.objects.get(code=category_name)
                    obj.category = category
                except Category.DoesNotExist:
                    # TODO log it in sentry
                    pass

    def process_obj(self, obj):
        if obj.current_node_id:
            current_node = self.graph.node[obj.current_node_id]
            current_node['id'] = obj.current_node_id

            nodes = obj.nodes or []
            nodes.append(current_node)
            obj.nodes = nodes

            children = self.graph.successors(obj.current_node_id)
            if len(children) == 1:
                obj.current_node_id = children[0]
                self.process_obj(obj)

    def save_object(self, obj, **kwargs):
        if obj.current_node_id:
            self.process_obj(obj)
            self._set_state(obj)

        return super(DiagnosisSerializer, self).save_object(obj, **kwargs)

    class Meta:
        model = DiagnosisTraversal
        fields = ('reference',
                  'nodes',
                  'choices',
                  'current_node_id',
                  'state',
                  'category')
