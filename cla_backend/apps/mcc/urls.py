from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import MCCCaseViewSet

case_split = MCCCaseViewSet.as_view({"post": "split"})
case_detailed = MCCCaseViewSet.as_view({"get": "detailed"})

urlpatterns = patterns(
    "",
    url(r"^case/(?P<reference>[A-Z|\d]{2}-\d{4}-\d{4})/split/$", case_split, name="case-split"),
    url(r"^case/(?P<reference>[A-Z|\d]{2}-\d{4}-\d{4})/detailed/$", case_detailed, name="case-detailed"),
)
