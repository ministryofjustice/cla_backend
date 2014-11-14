from django.db import models

from model_utils.models import TimeStampedModel


class AccessAttemptManager(models.Manager):
    def delete_for_username(self, username):
        if not username:
            return

        self.filter(username=username).delete()

    def create_for_username(self, username):
        if not username:
            return

        return self.create(username=username)


class AccessAttempt(TimeStampedModel):
    username = models.CharField(max_length=255)

    objects = AccessAttemptManager()
