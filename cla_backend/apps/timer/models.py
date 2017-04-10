from django.db import models
from django.conf import settings
from django.db import connection
from django_statsd.clients import statsd
from django.utils.translation import ugettext_lazy as _

from legalaid.models import Case

from .managers import RunningTimerManager

DB_NOW = 'NOW()'


def postgres_now():
    """
    Uses postgres NOW() function for setting value in the database
    This is because on distributed system you can't guarantee that the 
    times across systems are the same. Because creates uses the 
    database time, so should the stoppet field to keep timings 
    consistent.

    Previously there have been time missmatches where stopped was less 
    than created which resulted in negative time spent on case.

    Function has been separated out for mocking in some of the tests.

    :return str: NOW(): 
    """
    return DB_NOW


class CurrentTimestampDateTimeField(models.DateTimeField):
    """
    Field class to allow using postgres NOW() function for setting a 
    field to a current timestamp
    """

    def get_db_prep_value(self, value, connection, prepared=False):
        return value if value == DB_NOW else \
            super(CurrentTimestampDateTimeField, self).get_db_prep_value(
                value, connection, prepared=False)


class Timer(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    stopped = CurrentTimestampDateTimeField(blank=True, null=True)
    linked_case = models.ForeignKey(Case, blank=True, null=True)
    cancelled = models.BooleanField(default=False)

    created = CurrentTimestampDateTimeField(_('created'), default=postgres_now,
                                            editable=False)
    modified = models.DateTimeField(_('modified'), auto_now=True,
                                    editable=False)

    objects = models.Manager()
    running_objects = RunningTimerManager()

    def __unicode__(self):
        return u'Timer created at %s' % self.created

    @classmethod
    def start(cls, user):
        statsd.incr('timer.start')
        timer, created = cls.objects.get_or_create(
            created_by=user, cancelled=False, stopped__isnull=True,
            defaults={'created_by': user})
        return timer

    def is_stopped(self):
        return self.stopped

    def stop(self, cancelled=False):
        statsd.incr('timer.stopped')
        if self.is_stopped():
            raise ValueError(u'The timer has already been stopped')

        last_log = self.log_set.order_by('created').last()  # get last log
        if not last_log and not cancelled:
            raise ValueError(u'You can\'t stop a timer without a log')

        # stop and update this model
        self.stopped = postgres_now()

        self.cancelled = cancelled
        if last_log:
            self.linked_case = last_log.case

        self.save()
        if self.linked_case:
            # update billable time on case
            cursor = connection.cursor()
            cursor.execute('''
                select sum(ceiling(EXTRACT(epoch FROM a.stopped-a.created)))
                    from timer_timer as a
                    where
                    a.cancelled = false and
                    a.stopped is not null and a.linked_case_id = %s''', [self.linked_case.id])
            total_billable_time, = cursor.fetchone()
            print total_billable_time
            if total_billable_time:
                self.linked_case.billable_time = total_billable_time
                if total_billable_time:
                    statsd.timing('timer.total_time', total_billable_time * 1000)
                self.linked_case.save(update_fields=['billable_time'])
