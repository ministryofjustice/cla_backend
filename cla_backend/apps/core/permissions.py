from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.core.cache import cache


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


class ClientIDPermission(BasePermission):
    """
    The request is authenticated as a user and the token used has the right scope
    """

    client_name = None

    def get_client_name(self, token):
        client_name = cache.get("cla.oauth_client_%s" % token.client_id)
        if not client_name:
            client_name = token.client.name
            cache.set("cla.oauth_client_%s" % token.client_id, client_name)
        return client_name

    def has_permission(self, request, view):
        token = request.auth
        read_only = request.method in SAFE_METHODS

        if not token:
            return False
        if hasattr(token, "client_id"):  # OAuth 2
            return self.client_name == self.get_client_name(token)
        assert False, (
            "TokenHasReadWriteScope requires the " "`OAuth2Authentication` authentication " "class to be used."
        )


class AllowNone(BasePermission):
    """
    Allow no access. Paranoid.
    Used as the default authentication class so that if we forget to set
    any permissions then we get permission denided instead of blowing the doors
    open.
    """

    def has_permission(self, request, view):
        return False
