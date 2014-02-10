from django.conf.urls import patterns, url, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'category', views.CategoryViewSet)
router.register(r'question', views.QuestionViewSet)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
