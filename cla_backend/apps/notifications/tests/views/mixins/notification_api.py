from rest_framework import status

from core.tests.mommy_utils import make_recipe
from core.tests.test_base import SimpleResourceAPIMixin


class NotificationAPIMixin(SimpleResourceAPIMixin):
    LOOKUP_KEY = "pk"
    API_URL_BASE_NAME = "notifications"
    RESOURCE_RECIPE = "notifications.notification"

    def setUp(self):
        super(NotificationAPIMixin, self).setUp()

        self.notifications = make_recipe("notifications.notification", _quantity=2)

        make_recipe("notifications.notification_out_of_time", _quantity=2)

    def test_get_allowed(self):
        """
        Ensure we can GET the list and it is ordered
        """
        # LIST
        response = self.client.get(self.list_url, HTTP_AUTHORIZATION=self.get_http_authorization())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [d["notification"] for d in response.data], ["Notification1", "Notification2", "Notification3"]
        )

        # DETAIL
        response = self.client.get(self.detail_url, HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["notification"], "Notification1")

    def test_methods_not_allowed(self):
        """
        Ensure that we can't POST, PUT or DELETE
        """
        # LIST
        self._test_post_not_allowed(self.list_url)
        self._test_put_not_allowed(self.list_url)
        self._test_delete_not_allowed(self.list_url)

        # DETAIL
        self._test_post_not_allowed(self.detail_url)
        self._test_put_not_allowed(self.detail_url)
        self._test_delete_not_allowed(self.detail_url)
