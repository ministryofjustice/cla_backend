from django.db import models
from model_utils.models import TimeStampedModel


class CaseArchived(TimeStampedModel):
    full_name = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    postcode = models.CharField(max_length=12, blank=True, null=True)
    laa_reference = models.BigIntegerField(
        null=True, blank=True, unique=True, editable=False
    )

    specialist_referred_to = models.TextField(null=True, blank=True)
    date_specialist_referred = models.DateTimeField(null=True, blank=True)
    date_specialist_closed = models.DateTimeField(null=True, blank=True)

    knowledgebase_items_used = models.TextField(null=True, blank=True)
    area_of_law = models.TextField(null=True, blank=True)
    in_scope = models.NullBooleanField(null=True, blank=True)
    financially_eligible = models.NullBooleanField(null=True, blank=True)

    outcome_code = models.TextField(null=True, blank=True)
    outcome_code_date = models.DateTimeField(null=True, blank=True)
    search_field = models.TextField(null=True, blank=True)
