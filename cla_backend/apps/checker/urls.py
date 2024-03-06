from django.conf.urls import patterns, url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"diagnosis", views.DiagnosisViewSet, base_name="diagnosis")
router.register(r"category", views.CategoryViewSet)
router.register(r"case", views.CaseViewSet)
router.register(r"organisation", views.ArticleViewSet)
router.register(r"eligibility_check", views.EligibilityCheckViewSet, base_name="eligibility_check")
router.register(r"reasons_for_contacting", views.ReasonForContactingViewSet, base_name="reasons_for_contacting")
router.register(r"callback_time_slots", views.CallbackTimeSlotViewSet, base_name="callback_time_slots")

urlpatterns = patterns("", url(r"^", include(router.urls)))
