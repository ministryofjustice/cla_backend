from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^provider-closure-volume/$', views.provider_closure_volume,
        name="provider_closure_volume"),
    url(r'^operator-closure-volume/$', views.operator_closure_volume,
        name="operator_closure_volume"),
    url(r'^operator-create-volume/$', views.operator_create_volume,
        name="operator_create_volume"),
    url(r'^operator-avg-duration/$', views.operator_avg_duration,
        name="operator_avg_duration"),
    url(r'^reallocation/$', views.reallocation,
        name="reallocation"),
    url(r'^duplicate-matters/$', views.duplicate_matters,
        name="duplicate_matters"),

)
