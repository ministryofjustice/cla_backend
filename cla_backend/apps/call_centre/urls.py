from core.drf.router import NestedCLARouter
from django.conf.urls import patterns, url, include
from rest_framework import routers

print 'call_centre.urls loaded'
from . import views

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'provider/rota', views.OutOfHoursRotaViewSet)
router.register(r'provider', views.ProviderViewSet)
router.register(r'eligibility_check', views.EligibilityCheckViewSet, base_name='eligibility_check')
router.register(r'case', views.CaseViewSet)
router.register(r'user', views.UserViewSet, base_name='user')
router.register(r'personal_details', views.PersonalDetailsViewSet)
router.register(r'event', views.EventViewSet, base_name='event')
router.register(r'thirdparty_details', views.ThirdPartyDetailsViewSet)
router.register(r'adaptation_details', views.AdaptationDetailsViewSet)

case_router = NestedCLARouter(router, 'case', lookup='case')
case_router.register(r'eligibility_check', views.EligibilityCheckViewSet)
case_router.register(r'personal_details', views.PersonalDetailsViewSet)
case_router.register(r'adaptation_details', views.AdaptationDetailsViewSet)


urlpatterns = patterns('',
    url(r'', include(case_router.urls)),
    url(r'', include(router.urls)),
)

