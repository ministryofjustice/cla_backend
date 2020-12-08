import logging

from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now, localtime
from django.utils.formats import date_format

logger = logging.getLogger(__name__)


email_template = u"""
Specialist user {0} at {1}:

Username: {2}
Provider: {3}
Is manager: {4}
"""


def log_staff_created(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "Specialist user created",
            extra={
                "USERNAME": instance.user.username,
                "PROVIDER": instance.provider.name,
                "IS_MANAGER": unicode(instance.is_manager),
            },
        )

        message = email_template.format(
            "created",
            date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
            instance.user.username,
            instance.provider.name,
            unicode(instance.is_manager),
        )
        send_mail(
            "Specialist user added",
            message,
            settings.EMAIL_FROM_ADDRESS,
            settings.OPERATOR_USER_ALERT_EMAILS,
            fail_silently=True,
        )


def log_staff_modified(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    logger.info(
        "Specialist user modified",
        extra={
            "USERNAME": instance.user.username,
            "PROVIDER": instance.provider.name,
            "IS_MANAGER": unicode(instance.is_manager),
        },
    )

    message = email_template.format(
        "modified",
        date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
        instance.user.username,
        instance.provider.name,
        unicode(instance.is_manager),
    )
    send_mail(
        "Specialist user modified",
        message,
        settings.EMAIL_FROM_ADDRESS,
        settings.OPERATOR_USER_ALERT_EMAILS,
        fail_silently=True,
    )
