from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'eligibility_check', views.EligibilityCheckViewSet,
    base_name='eligibility_check'
)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
