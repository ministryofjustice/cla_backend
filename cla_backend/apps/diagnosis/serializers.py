import logging

from rest_framework.exceptions import ParseError
from rest_framework.fields import ChoiceField, SerializerMethodField
from rest_framework.relations import SlugRelatedField

from cla_common.constants import DIAGNOSIS_SCOPE

from core.serializers import ClaModelSerializer
from diagnosis.models import DiagnosisTraversal

from legalaid.models import Category, MatterType

from .graph import graph
from .utils import is_terminal, is_pre_end_node, get_node_scope_value

logger = logging.getLogger(__name__)


class DiagnosisSerializer(ClaModelSerializer):
    choices = SerializerMethodField('get_choices')
    nodes = SerializerMethodField('get_nodes')
    current_node_id = ChoiceField(choices=[])
    category = SlugRelatedField('category', slug_field='code', required=False)
    matter_type1 = SlugRelatedField('matter_type1', slug_field='code', required=False)
    matter_type2 = SlugRelatedField('matter_type2', slug_field='code', required=False)
    version_in_conflict = SerializerMethodField('is_version_in_conflict')

    def __init__(self, *args, **kwargs):
        # self.full_nodes_dump = kwargs.pop('full', False)
        super(DiagnosisSerializer, self).__init__(*args, **kwargs)
        self.graph = self._get_graph()

        nodes_choices = self._get_nodes()
        self.fields['current_node_id'].choices = [
            (node['id'], node['label']) for node in nodes_choices
        ]
        self.fields['current_node_id'].required = bool(nodes_choices)

    def _get_graph(self):
        return graph

    def is_version_in_conflict(self, request):
        if not self.object:
            return False

        if not self.object.is_state_unknown():
            return False

        return self.object.graph_version != self.graph.graph['version']

    def get_choices(self, request):
        return self._get_nodes()

    def get_nodes(self, request):
        if not self.object:
            return []

        nodes = self.object.nodes
        # this is just so that we don't show the INSCOPE / OUTOFSCOPE node
        # in the interface, nothing else clever happening
        # if not self.full_nodes_dump:
        #     if nodes and is_terminal(self.graph, nodes[-1]['id']):
        #         nodes = nodes[:-1]

        return nodes

    def _get_nodes(self, request=None):
        if self.is_version_in_conflict(request):
            return []

        if not self.object or not self.object.is_state_unknown():
            return []

        current_node_id = self.object.current_node_id or 'start'

        # populating choices
        children = self.graph.successors(current_node_id)
        nodes = []
        for child_id in children:
            node = self.graph.node[child_id].copy()
            node['id'] = child_id
            nodes.append(node)
        # nodes = [(node_id, self.graph.node[node_id])
        #          for node_id in children]
        nodes = sorted(nodes, key=lambda x: x['order'])
        return nodes

    def get_context(self, obj):
        context = {}
        if obj.nodes:
            for node in obj.nodes:
                context.update(node['context'] or {})
        return context

    def _get_from_context(self, context, node_id):
        def get_category(category_code, node_id):
            if category_code:
                try:
                    return Category.objects.get(code=category_code)
                except Category.DoesNotExist:
                    # this should never happen as we unit test the diagnosis graph
                    logger.warning(
                        u'Category %s for diagnosis node id=%s not a valid option' % (
                            category_code, node_id
                        )
                    )
            return None

        def get_matter_type(matter_type_code, node_id):
            if matter_type_code:
                try:
                    return MatterType.objects.get(code=matter_type_code)
                except MatterType.DoesNotExist:
                    # this should never happen as we unit test the diagnosis graph
                    logger.warning(
                        u'MatterType %s for diagnosis node id=%s not a valid option' % (
                            matter_type_code, node_id
                        )
                    )
            return None

        category_code = context.get('category')
        matter_type1_code = context.get('matter-type-1')
        matter_type2_code = context.get('matter-type-2')

        return {
            'category': get_category(category_code, node_id),
            'matter_type1': get_matter_type(matter_type1_code, node_id),
            'matter_type2': get_matter_type(matter_type2_code, node_id),
        }

    def _set_state(self, obj):
        if is_terminal(self.graph, obj.current_node_id):
            obj.state = get_node_scope_value(self.graph, obj.current_node_id)

            context_data = self._get_from_context(
                self.get_context(obj), obj.current_node_id
            )
            obj.category = context_data['category']
            obj.matter_type1 = context_data['matter_type1']
            obj.matter_type2 = context_data['matter_type2']
        else:
            obj.state = DIAGNOSIS_SCOPE.UNKNOWN
            obj.category = None
            obj.matter_type1 = None
            obj.matter_type2 = None

    def process_obj(self, obj):
        if obj.current_node_id:
            current_node = self.graph.node[obj.current_node_id]
            current_node['id'] = obj.current_node_id

            # delete all nodes after current_node_id and add current not
            nodes = []
            for node in (obj.nodes or []):
                if node['id'] == obj.current_node_id:
                    break
                nodes.append(node)

            nodes.append(current_node)
            obj.nodes = nodes

            # if pre end node => process end node directly
            if is_pre_end_node(self.graph, obj.current_node_id):
                obj.current_node_id = self.graph.successors(obj.current_node_id)[0]
                self.process_obj(obj)
        else:
            obj.nodes = []

    def save_object(self, obj, **kwargs):
        if not obj.graph_version:
            obj.graph_version = self.graph.graph['version']

        # if obj.current_node_id:
        self.process_obj(obj)
        self._set_state(obj)

        return super(DiagnosisSerializer, self).save_object(obj, **kwargs)

    def move_up(self):
        """
        Moves up one node.
        If there are no nodes, it raises ParseError.
        If current node is end node, it moves up 2 nodes
        """
        nodes = self.object.nodes or []
        nodes_count = len(nodes)

        # no nodes => can't go up
        if not nodes_count:
            raise ParseError("Cannot move up, no nodes found")

        if nodes_count == 1:  # root node => 'reset' the traversal
            self.object.current_node_id = ''  # :-/
        else:
            pre_node_id = nodes[-2]['id']

            # if current node is end node => move up 2 nodes
            if is_pre_end_node(self.graph, pre_node_id) and nodes_count > 2:
                pre_node_id = nodes[-3]['id']

            self.object.current_node_id = pre_node_id

        self.save(force_update=True)

        return self.object

    class Meta:
        model = DiagnosisTraversal
        fields = ('reference',
                  'nodes',
                  'choices',
                  'current_node_id',
                  'state',
                  'category',
                  'matter_type1',
                  'matter_type2',
                  'version_in_conflict'
                  )
