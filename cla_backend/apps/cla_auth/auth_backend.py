from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class TokenAuthBackend(ModelBackend):
    def authenticate(self, entra_id_email):
        try:
            # Get the user or create one if they don't exist
            user = User.objects.get(email=entra_id_email, is_active=True)
            return user
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
