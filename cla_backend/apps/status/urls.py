from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^hello/', views.hello),
    url(r'^', views.status),
)
