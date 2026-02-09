from rest_framework.permissions import BasePermission


class CallCentreClientIDPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method == "OPTIONS" or (hasattr(request.user, "operator") and bool(request.user.operator))


class OperatorManagerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.operator.is_manager
