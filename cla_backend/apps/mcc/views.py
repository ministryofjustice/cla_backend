from __future__ import unicode_literals

from rest_framework.decorators import detail_route

from cla_provider.forms import SplitMCCCaseForm
from cla_provider.views import CaseViewSet


class MCCCaseViewSet(CaseViewSet):
    @detail_route(methods=["post"])
    def split(self, request, reference=None, **kwargs):
        return self._form_action(request, Form=SplitMCCCaseForm, form_kwargs={"request": request})
