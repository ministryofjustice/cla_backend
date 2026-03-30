from core.permissions import ClientIDPermission
from rest_framework.permissions import BasePermission
from cla_auth.constants import OPERATOR_ROLE, OPERATOR_MANAGER_ROLE


class CallCentreClientIDPermission(ClientIDPermission):
    entra_roles = [OPERATOR_ROLE, OPERATOR_MANAGER_ROLE]
    client_name = "operator"


class OperatorManagerPermission(BasePermission):
    def has_permission(self, request, view):

        return request.user.operator.is_manager
