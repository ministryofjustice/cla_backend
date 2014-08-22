from django.template.defaultfilters import striptags

from cla_common.constants import DIAGNOSIS_SCOPE


def is_terminal(digraph, g_node_id):
    """

    :param digraph: a networkx DiGraph or subclass (MultiDigraph)
    :param g_node_id: a node id
    :return: if node is terminal
    """
    if not g_node_id:
        return False
    return not bool(digraph.successors(g_node_id))


def is_pre_end_node(digraph, g_node_id):
    children = digraph.successors(g_node_id)
    if len(children) == 1 and is_terminal(digraph, children[0]):
        return True
    return False


def get_node_scope_value(digraph, g_node_id):
    if not is_terminal(digraph, g_node_id):
        return None

    node = digraph.node[g_node_id]
    label = striptags(node['label']+"    ").strip()

    return DIAGNOSIS_SCOPE.CHOICES_CONST_DICT.get(
        label, DIAGNOSIS_SCOPE.UNKNOWN
    )
