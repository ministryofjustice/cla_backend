from django.db import models
from django.core.exceptions import MultipleObjectsReturned


class RunningTimerManager(models.Manager):
    def get_query_set(self):
        qs = super(RunningTimerManager, self).get_query_set()
        return qs.filter(stopped__isnull=True, cancelled=False)

    def get_by_user(self, user_pk):
        timers = list(self.filter(created_by=user_pk))

        if len(timers) > 1:
            raise MultipleObjectsReturned()

        return timers[0]
