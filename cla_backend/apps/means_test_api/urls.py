from cla_backend.libs.django_compat import patterns, url

from . import views

urlpatterns = patterns("", url(r"^means_test/$", views.eligibility_batch_check, name="means_test"))
