from django.db import models

from model_utils.models import TimeStampedModel


class AccessAttempt(TimeStampedModel):
    username = models.CharField(max_length=255)
