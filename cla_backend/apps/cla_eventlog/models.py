from django.db import models
from jsonfield import JSONField
from django.conf import settings
from django_statsd.clients import statsd

from model_utils.models import TimeStampedModel

from timer.models import Timer

from .constants import LOG_LEVELS, LOG_TYPES


class Log(TimeStampedModel):
    case = models.ForeignKey('legalaid.Case')
    timer = models.ForeignKey(Timer, null=True, blank=True)
    code = models.CharField(max_length=50)
    type = models.CharField(choices=LOG_TYPES.CHOICES, max_length=20)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS.CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    notes = models.TextField(null=True, blank=True)

    # patch is a json field with the following structure:
    # {
    #   "serializer": "<...serializerClass...>"
    #   "forwards": <...jsonpatch...>,
    #   "backwards": <...jsonpatch...>
    # }
    # where <...jsonpatch...> is a RFC6903 json patch obj
    # and <...serializerClass...> is the serializer used to
    # to create this pair of patches.

    patch = JSONField(null=True, blank=True)
    context = JSONField(null=True, blank=True, help_text='Field to store extra event data for reporting')

    def __unicode__(self):
        return u'%s - %s:%s' % (self.case, self.type, self.code)

    def save(self, *args, **kwargs):
        super(Log, self).save(*args, **kwargs)
        if self.type == LOG_TYPES.OUTCOME and self.level >= LOG_LEVELS.HIGH:
            self.case.outcome_code = self.code
            self.case.level = self.level
            self.case.outcome_code_id = self.pk
            self.case.save(update_fields=["level", "outcome_code_id", "outcome_code", "modified"])

        if self.code == 'CASE_VIEWED' and hasattr(self.created_by, 'staff'):
            self.case.view_by_provider(self.created_by.staff.provider)
        statsd.incr('outcome.%s' % self.code)


    class Meta:
        ordering = ['-created']
