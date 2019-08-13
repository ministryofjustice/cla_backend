from django.shortcuts import get_object_or_404

from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.permissions import ClientIDPermission
from legalaid.models import Case
from .utils.organisation import case_organisation_matches_user_organisation
from .utils.organisation.exceptions import OrganisationMatchException


class CallCentreClientIDPermission(ClientIDPermission):
    client_name = "operator"


class OperatorManagerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.operator.is_manager


class OperatorOrganisationPermission(CallCentreClientIDPermission):
    def has_permission(self, request, view, *args, **kwargs):
        has_permission = super(OperatorOrganisationPermission, self).has_permission(request, view)
        if not has_permission:
            return False

        if request.method in SAFE_METHODS:
            return True

        case = get_object_or_404(Case, reference=view.kwargs.get("case_reference"))
        try:
            has_permission = case_organisation_matches_user_organisation(case, request.user)
        except OrganisationMatchException:
            return True

        return has_permission
