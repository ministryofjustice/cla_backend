from django.db import models
from django.db.models.signals import post_save, pre_save

from .signals import log_operator_created, log_operator_modified
from model_utils.models import TimeStampedModel


class Operator(TimeStampedModel):
    user = models.OneToOneField('auth.User')
    is_manager = models.BooleanField(default=False)
    is_cla_superuser = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

    @property
    def is_cla_superuser_or_manager(self):
        return self.is_manager or self.is_cla_superuser

    def save(self, *args, **kwargs):
        # if is_cla_superuser == True then
        #   set is_manager to True as well
        if self.is_cla_superuser:
            self.is_manager = True

        super(Operator, self).save(*args, **kwargs)

        # is_staff should be True for op managers / cla superusers
        # and False otherwise
        is_special_user = self.is_cla_superuser_or_manager
        if self.user.is_staff != is_special_user:
            self.user.is_staff = is_special_user
            self.user.save(update_fields=['is_staff'])


post_save.connect(log_operator_created, sender=Operator)
pre_save.connect(log_operator_modified, sender=Operator)
