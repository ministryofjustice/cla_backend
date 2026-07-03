import logging

logger = logging.getLogger(__name__)


def log_user_created(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "User created",
            extra={
                "USER_ID": instance.pk,
                "IS_STAFF": str(instance.is_staff),
                "IS_ACTIVE": str(instance.is_active),
                "IS_SUPERUSER": str(instance.is_superuser),
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
            "USER_ID": instance.pk,
            "IS_STAFF": str(instance.is_staff),
            "IS_ACTIVE": str(instance.is_active),
            "IS_SUPERUSER": str(instance.is_superuser),
        },
    )
