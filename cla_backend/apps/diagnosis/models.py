import json
from jsonfield import JSONField
from model_utils.models import TimeStampedModel

from uuidfield import UUIDField


class DiagnosisTraversal(TimeStampedModel):
    reference = UUIDField(auto=True, unique=True)
    nodes = JSONField(null=True, blank=True)
    current_node = JSONField(null=True, blank=True)

    @property
    def current_node(self):
        return self.get_current_node()

    @current_node.setter
    def current_node(self, val):
        pass

    def get_nodes(self):
        return json.loads(self.nodes) if self.nodes else None

    def get_current_node(self):
        nodes = self.get_nodes()
        if nodes:
            return nodes[-1]
        return None