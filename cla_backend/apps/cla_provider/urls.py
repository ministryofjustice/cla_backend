from django.conf.urls import patterns, url, include

from rest_framework import routers

from core.drf.router import NestedSimpleRouter, NestedCLARouter

from . import views


router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'case', views.CaseViewSet)
router.register(r'user', views.UserViewSet, base_name='user')
router.register(r'event', views.EventViewSet, base_name='event')

# router.register(r'knowledgebase/article', views.ArticleViewSet)
# router.register(r'knowledgebase/category', views.ArticleCategoryViewSet)
router.register(r'adaptations', views.AdaptationDetailsMetadataViewSet,
                base_name='adaptations-metadata')
router.register(r'mattertype', views.MatterTypeViewSet)
router.register(r'mediacode', views.MediaCodeViewSet)

case_one2one_router = NestedCLARouter(router, 'case', lookup='case')
case_one2one_router.register(r'eligibility_check', views.EligibilityCheckViewSet, base_name='eligibility_check')
case_one2one_router.register(r'personal_details', views.PersonalDetailsViewSet)
case_one2one_router.register(r'adaptation_details', views.AdaptationDetailsViewSet)
case_one2one_router.register(r'thirdparty_details', views.ThirdPartyDetailsViewSet)
case_one2one_router.register(r'diagnosis', views.DiagnosisViewSet, base_name='diagnosis')

case_one2many_router = NestedSimpleRouter(router, r'case', lookup='case')

case_one2many_router.register(r'feedback', views.FeedbackViewSet)
case_one2many_router.register(r'logs', views.LogViewSet)

urlpatterns = patterns('',
    url(r'^', include(case_one2one_router.urls)),
    url(r'^', include(case_one2many_router.urls)),
    url(r'^', include(router.urls)),
)
