from core.tests.test_base import CLAOperatorAuthBaseApiTestMixin
from django.conf.urls import patterns
from django.contrib.auth.models import User
from django.http import HttpResponse
from provider.oauth2.models import Client, AccessToken
from rest_framework import status

from rest_framework.authentication import OAuth2Authentication

from rest_framework.test import APIClient
from rest_framework.views import APIView
from django.test import TestCase

from .. import permissions

class MockView(APIView):
    permission_classes = (permissions.CallCentreClientIDPermission,)

    def get(self, request):
        return HttpResponse({'a': 1, 'b': 2, 'c': 3})

    def post(self, request):
        return HttpResponse({'a': 1, 'b': 2, 'c': 3})

    def put(self, request):
        return HttpResponse({'a': 1, 'b': 2, 'c': 3})

urlpatterns = patterns('',
    (r'^mock_view/$', MockView.as_view(authentication_classes=[OAuth2Authentication]))
)


class CallCentreClientIDPermissionTestCase(CLAOperatorAuthBaseApiTestMixin, TestCase):
    urls = 'call_centre.tests.test_permissions'

    def test_oauth2_permission_ok(self):
        response = self.client.get('/mock_view/', HTTP_AUTHORIZATION='Bearer %s' % self.token.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_oauth2_permission_fail_if_no_token(self):
        response = self.client.get('/mock_view/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_oauth2_permission_fail_if_wrong_client_id_token(self):
        new_client = Client.objects.create(
            user=self.user,
            name='test2',
            client_type=0,
            client_id='not_call_centre',
            client_secret='secret',
            url='http://localhost/',
            redirect_uri='http://localhost/redirect'
        )
        new_token = AccessToken.objects.create(
            user=self.user,
            client=new_client,
            token='token2',
            scope=0
        )
        response = self.client.get('/mock_view/', HTTP_AUTHORIZATION='Bearer %s' % new_token.token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
