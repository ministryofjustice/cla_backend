import logging

from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now, localtime
from django.utils.formats import date_format
from govuk_notify.api import GovUkNotify

logger = logging.getLogger(__name__)


def log_operator_created(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "Operator user created",
            extra={
                "USERNAME": instance.user.username,
                "IS_MANAGER": unicode(instance.is_manager),
                "IS_CLA_SUPERUSER": unicode(instance.is_cla_superuser),
            },
        )
        try:
            email = GovUkNotify()
            for address in settings.OPERATOR_USER_ALERT_EMAILS:
                email.send_email(
                    email_address=address,
                    template_id="48ce3539-48f3-4b2d-9931-2a57f89a521f",
                    personalisation={
                        'added_or_modified': 'added',
                        'datetime': date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
                        'username': instance.user.username,
                        'is_manager': unicode(instance.is_manager),
                        'is_cla_superuser': unicode(instance.is_cla_superuser)
                    },
                )
        except:
            pass

def log_operator_modified(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    logger.info(
        "Operator user modified",
        extra={
            "USERNAME": instance.user.username,
            "IS_MANAGER": unicode(instance.is_manager),
            "IS_CLA_SUPERUSER": unicode(instance.is_cla_superuser),
        },
    )
    try:
        email = GovUkNotify()
        for address in settings.OPERATOR_USER_ALERT_EMAILS:
            email.send_email(
                email_address=address,
                template_id="48ce3539-48f3-4b2d-9931-2a57f89a521f",
                personalisation={
                    'added_or_modified': 'modified',
                    'datetime': date_format(localtime(now()), "SHORT_DATETIME_FORMAT"),
                    'username': instance.user.username,
                    'is_manager': unicode(instance.is_manager),
                    'is_cla_superuser': unicode(instance.is_cla_superuser)
                },
            )
    except:
        pass