from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^provider-closure-volume/$', views.provider_closure_volume, name="provider_closure_volume"),
    url(r'^operator-closure-volume/$', views.operator_closure_volume, name="operator_closure_volume")
)
