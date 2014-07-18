import json
from jsonfield import JSONField
from model_utils.models import TimeStampedModel

from uuidfield import UUIDField

from django.db import models


class DiagnosisTraversal(TimeStampedModel):
    reference = UUIDField(auto=True, unique=True)
    nodes = JSONField(null=True, blank=True)
    current_node_id = models.CharField(blank=True, max_length=50)

    def get_nodes(self):
        return json.loads(self.nodes) if self.nodes else None

    # def get_current_node(self):
    #     nodes = self.get_nodes()
    #     if nodes:
    #         return nodes[-1]
    #     return None