from django.conf.urls import patterns, url

from . import views
from . import api


urlpatterns = patterns(
    "",
    url(r"^api/exports/$", api.ExportListView.as_view(), name="exports"),
    url(r"^api/exports/(?P<pk>[0-9]+)/$", api.ExportListView.as_view(), name="exports"),
    url(r"^exports/download/(?P<file_name>[A-Za-z0-9-_\.]+)$", views.download_file, name="exports"),
    url(
        r"^mi-provider-allocation-extract/$",
        views.mi_provider_allocation_extract,
        name="mi_provider_allocation_extract",
    ),
    url(r"^mi-case-extract/$", views.mi_case_extract, name="mi_case_extract"),
    url(
        r"^mi-case-view-audit-log-extract/$",
        views.mi_case_view_audit_log_extract,
        name="mi_case_view_audit_log_extract",
    ),
    url(
        r"^mi-complaint-view-audit-log-extract/$",
        views.mi_complaint_view_audit_log_extract,
        name="mi_complaint_view_audit_log_extract",
    ),
    url(r"^mi-feedback-extract/$", views.mi_feedback_extract, name="mi_feedback_extract"),
    url(r"^mi-duplicate-case-extract/$", views.mi_duplicate_case_extract, name="mi_duplicate_case_extract"),
    url(r"^mi-contacts-per-case-extract/$", views.mi_contacts_extract, name="mi_contacts_extract"),
    url(r"^mi-alternative-help-extract/$", views.mi_alternative_help_extract, name="mi_alternative_help_extract"),
    url(r"^mi-survey-extract/$", views.mi_survey_extract, name="mi_survey_extract"),
    url(r"^mi-cb1-extract/$", views.mi_cb1_extract, name="mi_cb1_extract"),
    url(r"^mi-cb1-extract-agilisys/$", views.mi_cb1_extract_agilisys, name="mi_cb1_extract_agilisys"),
    url(r"^mi-voice-extract/$", views.mi_voice_extract, name="mi_voice_extract"),
    url(r"^mi-digital-case-type-extract/$", views.mi_digital_case_type_extract, name="mi_digital_case_type_extract"),
    url(r"^mi-eod-extract/$", views.mi_eod_extract, name="mi_eod_extract"),
    url(r"^mi-comlpaints/$", views.mi_complaints, name="mi_complaints"),
    url(r"^mi-obiee-extract/$", views.mi_obiee_extract, name="mi_obiee_extract"),
    url(r"^metrics-report/$", views.metrics_report, name="metrics_report"),
)
