# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^legalaid/api/v1/', include('legalaid.urls', namespace='legalaid'))
    # url(r'^admin/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
