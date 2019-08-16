from django.shortcuts import get_object_or_404

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import MethodNotAllowed

from core.permissions import ClientIDPermission
from legalaid.models import Case, EODDetails
from complaints.models import Complaint
from .utils.organisation import case_organisation_matches_user_organisation
from .utils.organisation.exceptions import OrganisationMismatchException


class CallCentreClientIDPermission(ClientIDPermission):
    client_name = "operator"


class OperatorManagerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.operator.is_manager


class OperatorOrganisationCasePermission(CallCentreClientIDPermission):
    def has_permission(self, request, view, *args, **kwargs):
        has_permission = super(OperatorOrganisationCasePermission, self).has_permission(request, view)
        if not has_permission:
            return False

        if request.method not in view.allowed_methods:
            raise MethodNotAllowed(method=request.method)

        case = self.get_case(request, view)
        if not case:
            # Allow list and dashboard views
            return request.method in SAFE_METHODS

        try:
            has_permission = case_organisation_matches_user_organisation(case, request.user)
        except OrganisationMismatchException:
            # Operator or case creator does not have an organisation
            return True

        return has_permission

    def get_case(self, request, view):
        return get_object_or_404(Case, reference=view.kwargs.get("case_reference"))


class OperatorOrganisationComplaintPermission(OperatorOrganisationCasePermission):
    def get_case(self, request, view):
        case = None
        if "eod" in request.DATA:
            case = get_object_or_404(EODDetails, reference=request.DATA.get("eod")).case
        elif view.kwargs:
            case = get_object_or_404(Complaint, **view.kwargs).eod.case
        return case
