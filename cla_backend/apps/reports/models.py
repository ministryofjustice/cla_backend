from django.db import models
from model_utils.models import TimeStampedModel
from reports.constants import EXPORT_STATUS


class Export(TimeStampedModel):
    user = models.ForeignKey('auth.User')
    path = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=10, choices=EXPORT_STATUS)


class ExportLog(TimeStampedModel):
    export = models.ForeignKey('Exports', related_name='messages')
    message = models.TextField()
