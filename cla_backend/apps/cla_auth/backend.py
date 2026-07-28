from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend


class EntraAccessTokenAuthenticationBackend(ModelBackend):
    def authenticate(self, request=None, entra_id_email=None, **kwargs):
        if not entra_id_email:
            return None
        user = User.objects.get(email__iexact=entra_id_email, is_active=True)
        return user
