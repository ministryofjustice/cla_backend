from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
        url(r'^means_test/$', views.eligibility_batch_check, name='means_test'),
)
