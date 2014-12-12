from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^mi-case-extract/$',
        views.mi_case_extract,
        name="mi_case_extract"),
    url(r'^mi-feedback-extract/$',
        views.mi_feedback_extract,
        name="mi_feedback_extract"),
    url(r'^mi-contacts-per-case-extract/$',
        views.mi_contacts_extract,
        name="mi_contacts_extract"),
    url(r'^mi-alternative-help-extract/$',
        views.mi_alternative_help_extract,
        name="mi_alternative_help_extract"),
    url(r'^mi-survey-extract/$',
        views.mi_survey_extract,
        name="mi_survey_extract"),
    url(r'^mi-cb1-extract/$',
        views.mi_cb1_extract,
        name="mi_cb1_extract"),
    url(r'^mi-voice-extract/$',
        views.mi_voice_extract,
        name="mi_voice_extract"),
)
