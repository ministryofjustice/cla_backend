import logging

from django.conf import settings
from django.utils.timezone import now, localtime
from django.utils.formats import date_format
from govuk_notify.api import NotifyEmailOrchestrator

logger = logging.getLogger(__name__)


def log_staff_created(sender, instance, created, **kwargs):
    if created:
        log_staff_action("created", instance)


def log_staff_modified(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    log_staff_action("modified", instance)


def log_staff_action(action, instance):
    logger.info(
        "Specialist user {}".format(action),
        extra={
            "USERNAME": instance.user.username,
            "PROVIDER": instance.provider.name,
            "IS_MANAGER": unicode(instance.is_manager),
        },
    )

    email = NotifyEmailOrchestrator()
    for address in settings.OPERATOR_USER_ALERT_EMAILS:
        email.send_email(
            email_address=address,
            template_id=settings.GOVUK_NOTIFY_TEMPLATES["LOG_SPECIALIST_ACTION"],
            personalisation={
                "action": action,
                "datetime": date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
                "username": instance.user.username,
                "provider": instance.provider.name,
                "is_manager": unicode(instance.is_manager),
            },
        )
