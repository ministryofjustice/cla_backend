from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import connection

from model_utils.models import TimeStampedModel

from legalaid.models import Case

from .managers import RunningTimerManager


class Timer(TimeStampedModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    stopped = models.DateTimeField(blank=True, null=True)
    linked_case = models.ForeignKey(Case, blank=True, null=True)

    objects = models.Manager()
    running_objects = RunningTimerManager()

    def __unicode__(self):
        return u'Timer created at' % self.created

    @classmethod
    def start(cls, user):
        return cls.objects.create(created_by=user)

    def is_stopped(self):
        return self.stopped

    def stop(self):
        if self.is_stopped():
            raise ValueError(u'The timer has already been stopped')

        last_log = self.log_set.last()  # get last log
        if not last_log:
            raise ValueError(u'You can\'t stop a timer without a log')

        # stop and update this model
        self.stopped = timezone.now()  # stop
        self.linked_case = last_log.case

        self.save()

        # update billable time on case
        cursor = connection.cursor()
        cursor.execute('''update
    legalaid_case
set billable_time =
    (select sum(ceiling(EXTRACT(epoch FROM a.stopped-a.created)))
    from timer_timer as a
    where a.stopped is not null and linked_case_id = legalaid_case.id)
where id = %s''', [self.linked_case.id])