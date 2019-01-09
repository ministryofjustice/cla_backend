import logging

from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now, localtime
from django.utils.formats import date_format
from django_statsd.clients import statsd

logger = logging.getLogger(__name__)

email_template = u"""
Operator user {0} at {1}:

Username: {2}
Is manager: {3}
Is CLA Superuser: {4}
"""


def log_operator_created(sender, instance, created, **kwargs):
    if created:
        statsd.incr("operator.created")

        logger.info(
            "Operator user created",
            extra={
                "USERNAME": instance.user.username,
                "IS_MANAGER": unicode(instance.is_manager),
                "IS_CLA_SUPERUSER": unicode(instance.is_cla_superuser),
            },
        )

        message = email_template.format(
            "created",
            date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
            instance.user.username,
            unicode(instance.is_manager),
            unicode(instance.is_cla_superuser),
        )
        send_mail(
            "Operator user added",
            message,
            settings.EMAIL_FROM_ADDRESS,
            settings.OPERATOR_USER_ALERT_EMAILS,
            fail_silently=True,
        )


def log_operator_modified(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    statsd.incr("operator.modified")

    logger.info(
        "Operator user modified",
        extra={
            "USERNAME": instance.user.username,
            "IS_MANAGER": unicode(instance.is_manager),
            "IS_CLA_SUPERUSER": unicode(instance.is_cla_superuser),
        },
    )

    message = email_template.format(
        "modified",
        date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
        instance.user.username,
        unicode(instance.is_manager),
        unicode(instance.is_cla_superuser),
    )
    send_mail(
        "Operator user modified",
        message,
        settings.EMAIL_FROM_ADDRESS,
        settings.OPERATOR_USER_ALERT_EMAILS,
        fail_silently=True,
    )
