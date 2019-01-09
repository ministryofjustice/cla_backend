import mock


class MockedGraph(mock.MagicMock):
    def __init__(self, *args, **kwargs):
        """
                  start
                    |
                  _______
                |         |
                2a        2b
                |         |
         ___________       _____
        |           |           |
       3aa         3ab         3ba
                    |
                    INSCOPE
        """
        super(MockedGraph, self).__init__(*args, **kwargs)
        self.node = {
            "start": {"label": "start", "order": 1, "context": None, "help": None},
            "2a": {"label": "2a", "order": 1, "context": None, "help": None},
            "2b": {"label": "2b", "order": 1, "context": None, "help": None},
            "3aa": {"label": "3aa", "order": 1, "context": None, "help": None},
            "3ab": {"label": "3ab", "order": 1, "context": None, "help": None},
            "3ba": {"label": "3ba", "order": 1, "context": None, "help": None},
            "INSCOPE": {
                "label": "INSCOPE",
                "order": 1,
                "context": {"category": "debt", "matter-type-1": "mt1", "matter-type-2": "mt2"},
                "help": None,
            },
        }
        self.children = {"start": ["2a", "2b"], "2a": ["3aa", "3ab"], "2b": ["3ba"], "3ab": ["INSCOPE"]}
        self.graph = {"version": "v1"}

    def get_node_dict(self, node_id, short=False):
        node = self.node[node_id].copy()
        node["id"] = node_id

        if short:
            node = {"id": node["id"], "label": node["label"]}
        return node

    def successors(self, node_id):
        return self.children.get(node_id, [])
