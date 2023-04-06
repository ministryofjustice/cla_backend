from model_utils.models import TimeStampedModel
from django.db import models
from django.db.models import Q
from legalaid.models import PersonalDetails
from extended_choices import Choices


STATUS = Choices(
    # constant, db_id, friendly string
    ("OK", "ok", "OK"),
    ("FAIL", "fail", "Fail"),
)

ACTION = Choices(
    # constant, db_id, friendly string
    ("CHECK", "check", "Check"),
)

class DiversityDataCheck(TimeStampedModel):
    personal_details = models.OneToOneField(PersonalDetails)
    detail = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION)
    status = models.CharField(max_length=10, choices=STATUS)

    @classmethod
    def get_unprocessed_personal_data_qs(cls, action):
        return PersonalDetails.objects.prefetch_related('diversitydatacheck').filter(
            Q(diversitydatacheck__pk__isnull=True) | ~Q(diversitydatacheck__action=action), diversity__isnull=False
        ).order_by('created')
