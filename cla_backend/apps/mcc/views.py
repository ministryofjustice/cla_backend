from __future__ import unicode_literals

from rest_framework.decorators import detail_route
from rest_framework.response import Response as DRFResponse

from cla_provider.forms import SplitMCCCaseForm
from cla_provider.views import CaseViewSet

from mcc import serializers


class MCCCaseViewSet(CaseViewSet):
    @detail_route(methods=["post"])
    def split(self, request, reference=None, **kwargs):
        return self._form_action(request, Form=SplitMCCCaseForm, form_kwargs={"request": request})

    @detail_route()
    def detailed(self, *args, **kwargs):
        """
        Returns case with all nested details in a single call
        """
        case = self.get_object()
        serializer = serializers.DetailedCaseSerializer(instance=case)
        return DRFResponse(serializer.data)
