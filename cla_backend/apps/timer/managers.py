from django.db import models
from django.core.exceptions import MultipleObjectsReturned


class RunningTimerManager(models.Manager):
    def get_query_set(self):
        qs = super(RunningTimerManager, self).get_query_set()
        return qs.filter(stopped__isnull=True, cancelled=False)

    def get_by_user(self, user_pk):
        qs = self.filter(created_by=user_pk)

        if qs.count() > 1:
            raise MultipleObjectsReturned()

        return qs[0]
