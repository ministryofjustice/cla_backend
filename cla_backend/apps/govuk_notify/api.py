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
        """
        :param email_address: (str) - Email address of the receiver
        :param template_id: (str) - The GOV.UK Notify template id
        :param personalisation: (optional, dictionary) - The personalisation dictionary
        :return: send_api_request (bool) - Was the request sent, will return True if the request was made successfully
                                          will return False if the EMAIL_ORCHESTRATOR_URL is not set or
                                          the application is in TEST_MODE or DEBUG mode
        """
        if settings.TEST_MODE or settings.DEBUG:
            logger.info("Application is in TESTING mode, will not send the request")
            return False

        if not self.base_url:
            logger.error("EMAIL_ORCHESTRATOR_URL is not set, unable to send email")
            return False
        data = {"email_address": email_address, "template_id": template_id}
        if personalisation:
            data["personalisation"] = personalisation

        response = requests.post(self.url(), json=data)

        if response.status_code != 201:
            raise HTTPError(response)
        return True
