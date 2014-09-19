from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProviderPermission(BasePermission):
    """
    Check the request is being made by a provider user
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'staff') and bool(request.user.staff)

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

    def has_permission(self, request, view):
        token = request.auth
        read_only = request.method in SAFE_METHODS

        if not token:
            return False

        if hasattr(token, 'client_id'):  # OAuth 2
            return self.client_name == token.client.name
        assert False, ('TokenHasReadWriteScope requires the'
                        '`OAuth2Authentication` authentication '
                       'class to be used.')

class AllowNone(BasePermission):
    """
    Allow no access. Paranoid.
    Used as the default authentication class so that if we forget to set
    any permissions then we get permission denided instead of blowing the doors
    open.
    """
    def has_permission(self, request, view):
        return False

