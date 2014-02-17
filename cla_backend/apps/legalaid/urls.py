from django.conf.urls import patterns, url, include

from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from . import views

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'eligibility_check', views.EligibilityCheckViewSet, base_name='eligibility_check')
router.register(r'case', views.CaseViewSet)

eligibility_check_router = \
    NestedSimpleRouter(router,
                       'eligibility_check',
                       lookup='eligibility_check_')

eligibility_check_router.register(r'property',
                                  views.PropertyViewSet,
                                  base_name='property',
                                )


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^', include(eligibility_check_router.urls)),
)
