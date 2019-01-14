from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = patterns("", url("^access_token/?$", csrf_exempt(views.AccessTokenView.as_view()), name="access_token"))
