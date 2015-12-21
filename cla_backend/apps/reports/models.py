import os
from django.db import models
from django.db.models.signals import pre_delete

from model_utils.models import TimeStampedModel
from reports.constants import EXPORT_STATUS


class Export(TimeStampedModel):
    user = models.ForeignKey('auth.User')
    path = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=10, choices=EXPORT_STATUS)
    task_id = models.CharField(max_length=100)
    message = models.TextField()

    @property
    def link(self):
        if self.path:
            return '/admin/reports/exports/download/%s' % os.path.basename(self.path)


def delete_export_file(sender, instance=None, **kwargs):
    if instance.path:
        os.remove(instance.path)


pre_delete.connect(delete_export_file, sender=Export)
