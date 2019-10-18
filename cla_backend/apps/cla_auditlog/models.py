from django.db import models

from model_utils.models import TimeStampedModel
from extended_choices import Choices


class AuditLog(TimeStampedModel):
    ACTIONS = Choices(
        # constant, db_id, friendly string
        ("VIEWED", "VIEWED", "viewed")
    )
    user = models.ForeignKey("auth.User", blank=True, null=True)
    action = models.CharField(choices=ACTIONS, db_index=True, max_length=50)
