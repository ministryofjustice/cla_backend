from core.permissions import ClientIDPermission
from rest_framework.permissions import BasePermission


class CallCentreClientIDPermission(ClientIDPermission):
    client_name = "operator"
    scope = "Client.HelpLine"

    def has_permission(self, request, view):
        """
        By the time the user has reach here they could have gone through the old oauth2 authentication flow or
        the new entra authentication flow.

        When request.auth contains an audience string matching  settings.ENTRA_EXPECTED_AUDIENCE then they have gone
        through the new entra authentication flow.
        """
        if isinstance(request.auth, dict):
            scope = request.auth.get("scp".decode("utf-8"))
            return scope == self.scope

        return super(CallCentreClientIDPermission, self).has_permission(request, view)


class OperatorManagerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.operator.is_manager
