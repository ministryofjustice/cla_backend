from rest_framework.permissions import BasePermission


class IsProviderPermission(BasePermission):
    """
    Check the request is being made by a provider user.
    OPTIONS always allowed without authentication to support CORS requests
    """

    def has_permission(self, request, view):
        return request.method == "OPTIONS" or (hasattr(request.user, "staff") and bool(request.user.staff))

    def has_object_permission(self, request, view, obj):
        if not obj:
            return True
        else:
            return obj.provider == request.user.staff.provider


class AllowNone(BasePermission):
    """
    Allow no access. Paranoid.
    Used as the default authentication class so that if we forget to set
    any permissions then we get permission denided instead of blowing the doors
    open.
    """

    def has_permission(self, request, view):
        return False
