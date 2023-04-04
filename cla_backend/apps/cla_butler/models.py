from model_utils.models import TimeStampedModel
from django.db import models
from legalaid.models import PersonalDetails


class DiversityDataCheck(TimeStampedModel):
    personal_details = models.OneToOneField(PersonalDetails)
    detail = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=20)
    status = models.CharField(max_length=10)

    @classmethod
    def get_unprocessed_personal_data_qs(cls):
        return PersonalDetails.objects.prefetch_related('diversitydatacheck').filter(
            diversitydatacheck__pk__isnull=True, diversity__isnull=False
        ).order_by('created')
