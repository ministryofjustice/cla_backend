from cla_backend.libs.django_compat import patterns, url

from . import views

app_name = "means_test"

urlpatterns = patterns("", url(r"^means_test/$", views.eligibility_batch_check, name="means_test"))
