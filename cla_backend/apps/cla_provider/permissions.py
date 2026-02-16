from django.conf import settings
from core.permissions import ClientIDPermission


class CLAProviderClientIDPermission(ClientIDPermission):
    client_name = "staff"

    def has_permission(self, request, view):
        """
        By the time the user has reach here they could have gone through the old oauth2 authentication flow or
        the new entra authentication flow.

        When request.auth contains an audience string matching  settings.ENTRA_EXPECTED_AUDIENCE then they have gone
        through the new entra authentication flow.
        """

        audience = request.auth.get("aud")
        if audience == settings.ENTRA_EXPECTED_AUDIENCE:
            return request.method == "OPTIONS" or (hasattr(request.user, "staff") and bool(request.user.staff))

        return super(CLAProviderClientIDPermission, self).has_permission(request, view)
