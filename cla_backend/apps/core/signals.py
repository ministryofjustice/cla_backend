import logging

logger = logging.getLogger(__name__)


def log_user_created(sender, instance, created, **kwargs):
    logger.info(
        "User created",
        extra={
            "USERNAME": instance.username,
            "IS_STAFF": unicode(instance.is_staff),
            "IS_ACTIVE": unicode(instance.is_active),
            "IS_SUPERUSER": unicode(instance.is_superuser),
        },
    )


def log_user_modified(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    logger.info(
        "User modified",
        extra={
            "USERNAME": instance.username,
            "IS_STAFF": unicode(instance.is_staff),
            "IS_ACTIVE": unicode(instance.is_active),
            "IS_SUPERUSER": unicode(instance.is_superuser),
        },
    )
