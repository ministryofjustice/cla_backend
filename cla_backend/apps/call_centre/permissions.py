from core.permissions import ClientIDPermission
from rest_framework.permissions import BasePermission


class CallCentreClientIDPermission(ClientIDPermission):
    entra_roles = ["Civil Legal Advice Operator", "Civil Legal Advice - Helpline Operator", "Civil Legal Advice Access"]
    client_name = "operator"


class OperatorManagerPermission(BasePermission):
    def has_permission(self, request, view):
        
        return request.user.operator.is_manager
