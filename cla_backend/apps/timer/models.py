from django.db import models
from django.conf import settings
from django.utils import timezone

from model_utils.models import TimeStampedModel

from .managers import RunningTimerManager


class Timer(TimeStampedModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    stopped_at = models.DateTimeField(blank=True, null=True)

    objects = models.Manager()
    running_objects = RunningTimerManager()

    def __unicode__(self):
        return u'Timer created at' % self.created

    @classmethod
    def start(cls, user):
        return cls.objects.create(created_by=user)

    def is_stopped(self):
        return self.stopped_at

    def stop(self):
        if self.is_stopped():
            raise ValueError(u'The timer has already been stopped')

        self.stopped_at = timezone.now()
        self.save()
