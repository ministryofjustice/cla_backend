from rest_framework.permissions import BasePermission, SAFE_METHODS


class ClientIDPermission(BasePermission):
    """
    The request is authenticated as a user and the token used has the right scope
    """
    client_id = None

    def has_permission(self, request, view):
        token = request.auth
        read_only = request.method in SAFE_METHODS

        if not token:
            return False

        if hasattr(token, 'client_id'):  # OAuth 2
            return self.client_id == token.client.client_id
        assert False, ('TokenHasReadWriteScope requires the'
                        '`OAuth2Authentication` authentication '
                       'class to be used.')

