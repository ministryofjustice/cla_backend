import logging

from rest_framework.exceptions import ParseError
from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.relations import SlugRelatedField

from cla_common.constants import DIAGNOSIS_SCOPE

from core.serializers import ClaModelSerializer
from diagnosis.models import DiagnosisTraversal

from legalaid.models import Category, MatterType

from .graph import graph
from .utils import is_terminal, is_pre_end_node, get_node_scope_value, eval_promise

logger = logging.getLogger(__name__)


class DiagnosisSerializer(ClaModelSerializer):
    choices = SerializerMethodField()
    nodes = SerializerMethodField()
    current_node_id = CharField()
    category = SlugRelatedField(slug_field="code", required=False, queryset=Category.objects.all(), allow_null=True)
    matter_type1 = SlugRelatedField(
        slug_field="code", required=False, queryset=MatterType.objects.all(), allow_null=True
    )
    matter_type2 = SlugRelatedField(
        slug_field="code", required=False, queryset=MatterType.objects.all(), allow_null=True
    )
    version_in_conflict = SerializerMethodField("is_version_in_conflict")

    def __init__(self, *args, **kwargs):
        # self.full_nodes_dump = kwargs.pop('full', False)
        super(DiagnosisSerializer, self).__init__(*args, **kwargs)
        self.graph = self._get_graph()

        nodes_choices = self._get_nodes()
        self.fields["current_node_id"].choices = [(node["id"], node["label"]) for node in nodes_choices]
        self.fields["current_node_id"].required = bool(nodes_choices)

    def _get_graph(self):
        return graph

    def is_version_in_conflict(self, instance):
        if not instance:
            return False

        if not instance.is_state_unknown():
            return False

        return instance.graph_version != self.graph.graph["version"]

    def get_choices(self, instance):
        return self._get_nodes(instance)

    def get_nodes(self, instance):
        if not instance:
            return []

        nodes = instance.nodes
        # this is just so that we don't show the INSCOPE / OUTOFSCOPE node
        # in the interface, nothing else clever happening
        # if not self.full_nodes_dump:
        #     if nodes and is_terminal(self.graph, nodes[-1]['id']):
        #         nodes = nodes[:-1]

        return nodes

    def _get_nodes(self, instance=None):
        if self.is_version_in_conflict(instance):
            return []

        if not instance or not instance.is_state_unknown():
            return []

        current_node_id = instance.current_node_id or "start"

        # populating choices
        children = self.graph.successors(current_node_id)
        nodes = []
        for child_id in children:
            node = self.graph.node[child_id].copy()
            node["id"] = child_id
            nodes.append(node)
        # nodes = [(node_id, self.graph.node[node_id])
        #          for node_id in children]
        nodes = sorted(nodes, key=lambda x: x["order"])
        return nodes

    def get_context(self, nodes):
        context = {}
        if nodes:
            for node in nodes:
                context.update(node["context"] or {})
        return context

    def _get_from_context(self, context, node_id):
        def get_category(category_code, node_id):
            if category_code:
                try:
                    return Category.objects.get(code=category_code)
                except Category.DoesNotExist:
                    # this should never happen as we unit test the diagnosis graph
                    logger.warning(
                        u"Category %s for diagnosis node id=%s not a valid option" % (category_code, node_id)
                    )
            return None

        def get_matter_type(matter_type_code, node_id):
            if matter_type_code:
                try:
                    return MatterType.objects.get(code=matter_type_code)
                except MatterType.DoesNotExist:
                    # this should never happen as we unit test the diagnosis graph
                    logger.warning(
                        u"MatterType %s for diagnosis node id=%s not a valid option" % (matter_type_code, node_id)
                    )
            return None

        category_code = context.get("category")
        matter_type1_code = context.get("matter-type-1")
        matter_type2_code = context.get("matter-type-2")

        return {
            "category": get_category(category_code, node_id),
            "matter_type1": get_matter_type(matter_type1_code, node_id),
            "matter_type2": get_matter_type(matter_type2_code, node_id),
        }

    def _set_state(self, validated_data):
        current_node_id = validated_data.get("current_node_id")
        nodes = validated_data.get("nodes", [])
        if is_terminal(self.graph, current_node_id):
            validated_data["state"] = get_node_scope_value(self.graph, current_node_id)

            context_data = self._get_from_context(self.get_context(nodes), current_node_id)
            validated_data["category"] = context_data["category"]
            validated_data["matter_type1"] = context_data["matter_type1"]
            validated_data["matter_type2"] = context_data["matter_type2"]
        else:
            validated_data["state"] = DIAGNOSIS_SCOPE.UNKNOWN
            validated_data["category"] = None
            validated_data["matter_type1"] = None
            validated_data["matter_type2"] = None

    def process_obj(self, instance, validated_data):
        current_node_id = validated_data.get("current_node_id")
        if current_node_id:
            current_node = self.graph.node[current_node_id]
            current_node["id"] = current_node_id

            current_node = dict(map(lambda item: (item[0], eval_promise(item[1])), current_node.items()))

            # delete all nodes after current_node_id and add current not
            nodes = []
            if "nodes" in validated_data:
                current_nodes = validated_data["nodes"]
            else:
                current_nodes = getattr(instance, "nodes", []) or []
            for node in current_nodes:
                if node["id"] == current_node_id:
                    break
                nodes.append(node)

            nodes.append(current_node)
            validated_data["nodes"] = nodes

            # if pre end node => process end node directly
            if is_pre_end_node(self.graph, current_node_id):
                validated_data["current_node_id"] = self.graph.successors(current_node_id)[0]
                self.process_obj(instance, validated_data)
        else:
            validated_data["nodes"] = []

    def create(self, validated_data):
        validated_data["graph_version"] = self.graph.graph["version"]
        self.process_obj(self.instance, validated_data)
        self._set_state(validated_data)

        return super(DiagnosisSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if not instance.graph_version:
            instance.graph_version = self.graph.graph["version"]
        self.process_obj(instance, validated_data)
        self._set_state(validated_data)
        return super(DiagnosisSerializer, self).update(instance, validated_data)

    def move_up(self):
        """
        Moves up one node.
        If there are no nodes, it raises ParseError.
        If current node is end node, it moves up 2 nodes
        """
        validated_data = {}
        nodes = self.instance.nodes or []
        nodes_count = len(nodes)

        # no nodes => can't go up
        if not nodes_count:
            raise ParseError("Cannot move up, no nodes found")

        if nodes_count == 1:  # root node => 'reset' the traversal
            validated_data["current_node_id"] = ""  # :-/
        else:
            pre_node_id = nodes[-2]["id"]

            # if current node is end node => move up 2 nodes
            if is_pre_end_node(self.graph, pre_node_id) and nodes_count > 2:
                pre_node_id = nodes[-3]["id"]

            validated_data["current_node_id"] = pre_node_id

        if self.is_valid():
            self.validated_data.update(validated_data)
            self.save(force_update=True)

        return self.instance

    class Meta(object):
        model = DiagnosisTraversal
        fields = (
            "reference",
            "nodes",
            "choices",
            "current_node_id",
            "state",
            "category",
            "matter_type1",
            "matter_type2",
            "version_in_conflict",
        )
