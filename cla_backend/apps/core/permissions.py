from rest_framework.permissions import BasePermission
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
    entra_roles = []

    def get_client_name(self, token):
        client = token.application
        client_name = cache.get("cla.oauth_client_%s" % client.client_id)
        if not client_name:
            client_name = client.name
            cache.set("cla.oauth_client_%s" % client.client_id, client_name)
        return client_name

    def has_permission(self, request, view):
        has_permission = self.entra_has_permission(request, view)
        if has_permission is None:
            return self.legacy_has_permission(request, view)
        return has_permission

    def entra_has_permission(self, request, view):
        if isinstance(request.auth, dict):
            token_roles = request.auth.get("APP_ROLES")
            if token_roles is not None:
                if isinstance(token_roles, unicode):
                    token_roles = token_roles.encode('utf-8')
                if isinstance(token_roles, str):
                    token_roles = [token_roles]
                return all(role in self.entra_roles for role in token_roles)
        return None

    def legacy_has_permission(self, request, view):
        token = request.auth

        if not token:
            return False
        if hasattr(token, "application"):  # OAuth 2
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
