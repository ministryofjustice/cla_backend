from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend


class EntraAccessTokenAuthenticationBackend(ModelBackend):

    def authenticate(self, entra_id_email=None):
        user = User.objects.get(email=entra_id_email, is_active=True)
        return user
       
   