from django.db import models
from jsonfield import JSONField
from model_utils.models import TimeStampedModel
from django.conf import settings
from .constants import LOG_LEVELS, LOG_TYPES


class Log(TimeStampedModel):
    case = models.ForeignKey('legalaid.Case')
    code = models.CharField(max_length=20)
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

    def __unicode__(self):
        return u'%s - %s:%s' % (self.case, self.type, self.code)

    class Meta:
        ordering = ['-created']
