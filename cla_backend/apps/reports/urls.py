from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^provider-closure-volume/$', views.provider_closure_volume,
        name="provider_closure_volume"),
    url(r'^operator-closure-volume/$', views.operator_closure_volume,
        name="operator_closure_volume"),
    url(r'^operator-create-volume/$', views.operator_create_volume,
        name="operator_create_volume"),
    url(r'^all-cases/$', views.all_cases,
        name="all_cases"),
    url(r'^adaptations-counts/$', views.adaptation_counts,
        name="new_cases_with_adaptations"),
    url(r'^case-volume-avg-duration-operator-day/$',
        views.case_volume_avg_duration_by_operator_day,
        name="case_volume_and_avg_duration_by_operator_by_day"),
    url(r'^referred-cases-by-category/$',
        views.referred_cases_by_category,
        name="referred_cases_by_category"),
    url(r'^allocated-no-outcome/$',
        views.allocated_no_outcome,
        name="allocated_cases_with_no_outcome"),
)
