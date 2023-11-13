import logging
from notifications_python_client.errors import HTTPError
from django.conf import settings
import requests


logger = logging.getLogger(__name__)


class NotifyEmailOrchestrator(object):
    def __init__(self):
        self.base_url = None
        if settings.EMAIL_ORCHESTRATOR_URL:
            self.base_url = settings.EMAIL_ORCHESTRATOR_URL
        elif not settings.TEST_MODE and not settings.DEBUG:
            raise EnvironmentError("EMAIL_ORCHESTRATOR_URL is not set.")
        self.endpoint = "email"

    def url(self):
        base_url = self.base_url if self.base_url.endswith("/") else self.base_url + "/"

        return base_url + self.endpoint

    def send_email(self, email_address, template_id, personalisation=None):
        if not self.base_url:
            raise EnvironmentError("EMAIL_ORCHESTRATOR_URL is not set, unable to send email")
        data = {"email_address": email_address, "template_id": template_id}
        if personalisation:
            data["personalisation"] = personalisation

        response = requests.post(self.url(), json=data)

        if response.status_code != 201:
            raise HTTPError(response)
