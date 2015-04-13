from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views
from core.drf.router import NestedCLARouter, NestedSimpleRouter

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'case', views.CaseViewSet)
router.register(r'organisation', views.ArticleViewSet)
router.register(r'eligibility_check', views.EligibilityCheckViewSet, base_name='eligibility_check')

case_one2one_router = NestedCLARouter(router, 'case', lookup='case')
case_one2one_router.register(r'diagnosis', views.DiagnosisViewSet, base_name='diagnosis')

case_one2many_router = NestedSimpleRouter(router, r'case', lookup='case')

urlpatterns = patterns('',
    url(r'^', include(case_one2one_router.urls)),
    url(r'^', include(case_one2many_router.urls)),
    url(r'^', include(router.urls)),
)


