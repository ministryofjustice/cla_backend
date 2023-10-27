import logging
from notifications_python_client.notifications import NotificationsAPIClient
from notifications_python_client.errors import HTTPError
from django.conf import settings
import requests


logger = logging.getLogger(__name__)


class GovUkNotify(object):
    def __new__(cls):
        """
        If this feature flag is set rather than creating a GovUkNotify object
        a NotifyEmailOrchestrator object will be created instead, overloading the send_email method.
        """
        if settings.USE_EMAIL_ORCHESTRATOR_FLAG:
            return NotifyEmailOrchestrator()
        return super(GovUkNotify, cls).__new__(cls)

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
            self.notifications_client.send_email_notification(
                email_address=email_address,  # required string
                template_id=template_id,  # required UUID string
                personalisation=personalisation,
            )
        except HTTPError as error:
            logger.error("GovUkNotify error: {msg}".format(msg=str(error)))
            raise error


class NotifyEmailOrchestrator(object):
    def __init__(self):
        if not settings.EMAIL_ORCHESTRATOR_URL:
            if not settings.TEST_MODE and not settings.DEBUG:
                raise EnvironmentError("EMAIL_ORCHESTRATOR_URL is not set.")
        self.base_url = settings.EMAIL_ORCHESTRATOR_URL
        self.endpoint = "email"

    def url(self):
        base_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"

        return base_url + self.endpoint

    def send_email(self, email_address, template_id, personalisation=None):
        if not self.base_url:
            return
        data = {
            'email_address': email_address,
            'template_id': template_id,
        }
        if personalisation:
            data["personalisation"] = personalisation

        response = requests.post(self.url(), json=data)

        if response.status_code != 201:
            raise HTTPError(response)
