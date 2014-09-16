import logging

from django.contrib.auth.models import User
from django_statsd.clients import statsd

logger = logging.getLogger(__name__)


#@receiver(post_save, sender=User)
def log_user_created(sender, instance, created, **kwargs):
    if created:
        statsd.incr('user.created')

        logger.info('User created', extra={
            'USERNAME': instance.username,
            'IS_STAFF': unicode(instance.is_staff),
            'IS_ACTIVE': unicode(instance.is_active),
            'IS_SUPERUSER': unicode(instance.is_superuser)
        })


#@receiver(pre_save, sender=User)
def log_user_modified(sender, instance, **kwargs):
    try:
        User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    statsd.incr('user.modified')

    logger.info('User modified', extra={
        'USERNAME': instance.username,
        'IS_STAFF': unicode(instance.is_staff),
        'IS_ACTIVE': unicode(instance.is_active),
        'IS_SUPERUSER': unicode(instance.is_superuser)
    })
