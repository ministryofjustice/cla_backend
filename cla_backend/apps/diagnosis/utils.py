
def is_terminal(digraph, g_node_id):
    """

    :param digraph: a networkx DiGraph or subclass (MultiDigraph)
    :param g_node_id: a node id
    :return: if node is terminal
    """
    return not bool(digraph.successors(g_node_id))
