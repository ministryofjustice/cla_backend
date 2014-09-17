from django.db import models
from django.db.models.signals import post_save, pre_save

from .signals import log_operator_created, log_operator_modified
from model_utils.models import TimeStampedModel


class Operator(TimeStampedModel):
    user = models.OneToOneField('auth.User')
    is_manager = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username


post_save.connect(log_operator_created, sender=Operator)
pre_save.connect(log_operator_modified, sender=Operator)
