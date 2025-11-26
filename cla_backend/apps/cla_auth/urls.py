from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.views import RevokeTokenView

from . import views

urlpatterns = patterns(
    "",
    url(r"^access_token/?$", csrf_exempt(views.AccessTokenView.as_view()), name="access_token"),
    url(r'^revoke_token/$', RevokeTokenView.as_view(), name="revoke_token"),
)
