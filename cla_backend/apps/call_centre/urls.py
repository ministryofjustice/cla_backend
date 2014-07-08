from django.conf.urls import patterns, url, include

from rest_framework import routers
from core import routers as core_routers

from . import views

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'provider/rota', views.OutOfHoursRotaViewSet)
router.register(r'provider', views.ProviderViewSet)
router.register(r'eligibility_check', views.EligibilityCheckViewSet,
                base_name='eligibility_check')
router.register(r'case', views.CaseViewSet)
router.register(r'user', views.UserViewSet, base_name='user')
router.register(r'personal_details', views.PersonalDetailsViewSet)
router.register(r'event', views.EventViewSet, base_name='event')
router.register(r'thirdparty_details', views.ThirdPartyDetailsViewSet)
router.register(r'adaptation_details', views.AdaptationDetailsViewSet)
router.register(r'knowledgebase/article', views.ArticleViewSet)
router.register(r'knowledgebase/category', views.ArticleCategoryViewSet)

timer_router = core_routers.SingletonRouter()
timer_router.register(r'timer', views.TimerViewSet, base_name='timer')

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^', include(timer_router.urls)),
)
