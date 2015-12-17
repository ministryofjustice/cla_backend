from django.db import models
from model_utils.models import TimeStampedModel
from reports.constants import EXPORT_STATUS


class Export(TimeStampedModel):
    user = models.ForeignKey('auth.User')
    path = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=10, choices=EXPORT_STATUS)
    task_id = models.CharField(max_length=100)
    message = models.TextField()
