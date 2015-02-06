from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import Group

from model_utils.models import TimeStampedModel

from .signals import log_operator_created, log_operator_modified


OP_MANAGER_GROUP_NAME = 'Operator Managers'
LAA_CASEWORKER_GROUP_NAME = 'LAA Caseworker'
CLA_SUPERUSER_GROUP_NAME = 'CLA Superusers'

class Caseworker(TimeStampedModel):
    user = models.OneToOneField('auth.User')

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        obj = super(Caseworker, self).save(*args, **kwargs)
        group = Group.objects.get(name=LAA_CASEWORKER_GROUP_NAME)
        group.user_set.add(self.user)
        return obj

class Operator(TimeStampedModel):
    user = models.OneToOneField('auth.User')
    is_manager = models.BooleanField(default=False)
    is_cla_superuser = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.username

    @property
    def is_cla_superuser_or_manager(self):
        return self.is_manager or self.is_cla_superuser

    def _add_remove_from_group(self, group, add):
        if add:
            group.user_set.add(self.user)
        else:
            group.user_set.remove(self.user)

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

        # update the permissions
        self._add_remove_from_group(
            Group.objects.get(name=OP_MANAGER_GROUP_NAME),
            add=self.is_manager
        )

        self._add_remove_from_group(
            Group.objects.get(name=CLA_SUPERUSER_GROUP_NAME),
            add=self.is_cla_superuser
        )


post_save.connect(log_operator_created, sender=Operator)
pre_save.connect(log_operator_modified, sender=Operator)
