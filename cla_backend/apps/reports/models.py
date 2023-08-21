import os
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete

from model_utils.models import TimeStampedModel
from reports.constants import EXPORT_STATUS
from cla_backend.libs.aws.s3 import ReportsS3


class Export(TimeStampedModel):
    user = models.ForeignKey("auth.User")
    path = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=10, choices=EXPORT_STATUS)
    task_id = models.CharField(max_length=100)
    message = models.TextField()

    @property
    def link(self):
        if self.path:
            return "/admin/reports/exports/download/%s" % os.path.basename(self.path)


def delete_export_file(sender, instance=None, **kwargs):
    # check if there is a connection to aws, otherwise delete locally
    if settings.AWS_REPORTS_STORAGE_BUCKET_NAME:
        try:
            key = settings.EXPORT_DIR + os.path.basename(instance.path)
            ReportsS3.delete_file(settings.AWS_REPORTS_STORAGE_BUCKET_NAME, key)
        except (ValueError, AttributeError):
            pass
    else:
        filepath = settings.TEMP_DIR + "/" + os.path.basename(instance.path)
        # delete the file
        os.remove(filepath)


pre_delete.connect(delete_export_file, sender=Export)
