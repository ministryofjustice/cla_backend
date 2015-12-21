import boto
import os
from django.conf import settings
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
    conn = boto.connect_s3(
            settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.lookup(settings.AWS_STORAGE_BUCKET_NAME)
    k = bucket.get_key(settings.EXPORT_DIR + os.path.basename(instance.path))
    try:
        bucket.delete_key(k)
    except ValueError:
        pass


pre_delete.connect(delete_export_file, sender=Export)
