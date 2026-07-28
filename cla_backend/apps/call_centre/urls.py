from cla_backend.libs.django_compat import patterns, url, include
from rest_framework import routers

from core.drf.router import NestedSimpleRouter, NestedCLARouter, AdvancedSimpleRouter
from core import routers as core_routers

from . import views

app_name = "call_centre"

router = routers.DefaultRouter()
adv_router = AdvancedSimpleRouter()
router.register(r"category", views.CategoryViewSet)
router.register(r"provider/rota", views.OutOfHoursRotaViewSet)
router.register(r"provider", views.ProviderViewSet)
adv_router.register(r"case", views.CaseViewSet)
router.register(r"user", views.UserViewSet, basename="user")
router.register(r"event", views.EventViewSet, basename="event")
router.register(r"knowledgebase/article", views.ArticleViewSet)
router.register(r"knowledgebase/category", views.ArticleCategoryViewSet)
router.register(r"guidance/note", views.GuidanceNoteViewSet, basename="guidance_note")
router.register(r"notifications/notification", views.NotificationViewSet, basename="notifications")
router.register(r"adaptations", views.AdaptationDetailsMetadataViewSet, basename="adaptations-metadata")
router.register(r"mattertype", views.MatterTypeViewSet)
router.register(r"mediacode", views.MediaCodeViewSet)
router.register(r"contact_research_methods", views.ContactResearchMethodViewSet)
router.register(r"feedback", views.FeedbackViewSet)
router.register(r"case_archive", views.CaseArchivedViewSet)
router.register(r"csvupload", views.CSVUploadViewSet)
adv_router.register(r"complaints/complaint", views.ComplaintViewSet, basename="complaints")
router.register(r"complaints/category", views.ComplaintCategoryViewSet, basename="complaints-categories")

timer_router = core_routers.SingletonRouter()
timer_router.register(r"timer", views.TimerViewSet, basename="timer")

case_one2one_router = NestedCLARouter(adv_router, "case", lookup="case")
case_one2one_router.register(r"eligibility_check", views.EligibilityCheckViewSet, basename="eligibility_check")
case_one2one_router.register(r"personal_details", views.PersonalDetailsViewSet)
case_one2one_router.register(r"adaptation_details", views.AdaptationDetailsViewSet)
case_one2one_router.register(r"eod_details", views.EODDetailsViewSet)
case_one2one_router.register(r"thirdparty_details", views.ThirdPartyDetailsViewSet)
case_one2one_router.register(r"diagnosis", views.DiagnosisViewSet, basename="diagnosis")
case_one2one_router.register(r"scope_traversal", views.ScopeTraversalViewSet, basename="scope_traversal")

case_one2many_router = NestedSimpleRouter(adv_router, r"case", lookup="case")
case_one2many_router.register(r"logs", views.LogViewSet)
case_one2many_router.register(r"notes_history", views.CaseNotesHistoryViewSet)

complaint_one2many_router = NestedSimpleRouter(adv_router, r"complaints/complaint", lookup="complaint")
complaint_one2many_router.register(r"logs", views.ComplaintLogViewset)


urlpatterns = patterns(
    "",
    url(r"^complaints/constants/?$", views.ComplaintConstantsView.as_view()),
    url(r"^", include(complaint_one2many_router.urls)),
    url(r"^", include(case_one2one_router.urls)),
    url(r"^", include(case_one2many_router.urls)),
    url(r"^", include(adv_router.urls)),
    url(r"^", include(router.urls)),
    url(r"^", include(timer_router.urls)),
)
