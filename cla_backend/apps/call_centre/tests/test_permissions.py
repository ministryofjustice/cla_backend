import datetime

from django.conf.urls import patterns
from django.http import HttpResponse
from django.test import TestCase
from rest_framework import status
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from rest_framework.views import APIView

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from cla_backend.urls import urlpatterns as base_patterns
from oauth2_provider.models import Application, AccessToken
from .. import permissions


class MockView(APIView):
    permission_classes = (permissions.CallCentreClientIDPermission,)

    def get(self, request):
        return HttpResponse({"a": 1, "b": 2, "c": 3})

    def post(self, request):
        return HttpResponse({"a": 1, "b": 2, "c": 3})

    def put(self, request):
        return HttpResponse({"a": 1, "b": 2, "c": 3})


urlpatterns = base_patterns + patterns("", (r"^mock_view/$", MockView.as_view(authentication_classes=[OAuth2Authentication])))


class CallCentreClientIDPermissionTestCase(CLAOperatorAuthBaseApiTestMixin, TestCase):
    urls = "call_centre.tests.test_permissions"

    def test_oauth2_permission_ok(self):
        response = self.client.get("/mock_view/", HTTP_AUTHORIZATION="Bearer %s" % self.token.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_oauth2_permission_fail_if_no_token(self):
        response = self.client.get("/mock_view/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_oauth2_permission_fail_if_wrong_client_id_token(self):
        new_client = Application.objects.create(
            user=self.user,
            name="test2",
            client_type=0,
            client_id="not_call_centre",
            client_secret="secret",
            redirect_uris="http://localhost/redirect",
            authorization_grant_type="password",
        )
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=2)
        new_token = AccessToken.objects.create(user=self.user, application=new_client, token="token2", scope=0, expires=expiry_date)
        response = self.client.get("/mock_view/", HTTP_AUTHORIZATION="Bearer %s" % new_token.token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
