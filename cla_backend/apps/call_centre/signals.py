import logging

from django.conf import settings
from django.utils.timezone import now, localtime
from django.utils.formats import date_format
from govuk_notify.api import GovUkNotify

logger = logging.getLogger(__name__)


def log_operator_created(sender, instance, created, **kwargs):
    if created:
        log_operator_action("added", instance)


def log_operator_modified(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    log_operator_action("modified", instance)


def log_operator_action(action, instance):
    logger.info(
        "Operator user {}".format(action),
        extra={
            "USERNAME": instance.user.username,
            "IS_MANAGER": unicode(instance.is_manager),
            "IS_CLA_SUPERUSER": unicode(instance.is_cla_superuser),
        },
    )

    email = GovUkNotify()
    for address in settings.OPERATOR_USER_ALERT_EMAILS:
        email.send_email(
            email_address=address,
            template_id=settings.GOVUK_NOTIFY_TEMPLATES["LOG_OPERATOR_ACTION"],
            personalisation={
                "added_or_modified": action,
                "datetime": date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
                "username": instance.user.username,
                "is_manager": unicode(instance.is_manager),
                "is_cla_superuser": unicode(instance.is_cla_superuser),
            },
        )
