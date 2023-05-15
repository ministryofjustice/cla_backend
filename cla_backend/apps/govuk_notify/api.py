import logging
from notifications_python_client.notifications import NotificationsAPIClient
from notifications_python_client.errors import HTTPError

from django.conf import settings


logger = logging.getLogger(__name__)


class GovUkNotify(object):
    def __init__(self):
        self.notifications_client = None
        if settings.GOVUK_NOTIFY_API_KEY:
            self.notifications_client = NotificationsAPIClient(settings.GOVUK_NOTIFY_API_KEY)
        elif not settings.TEST_MODE and not settings.DEBUG:
            raise ValueError("Missing API Key for GOVUK Notify")

    def send_email(self, email_address, template_id, personalisation):
        if not self.notifications_client:
            return
        try:
            response = self.notifications_client.send_email_notification(
                email_address=email_address,  # required string
                template_id=template_id,  # required UUID string
                personalisation=personalisation,
            )
        except HTTPError as error:
            logger.error("GovUkNotify error: {msg}".format(msg=str(error)))
            raise error
        return response
