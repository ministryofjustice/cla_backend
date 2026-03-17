import jwt,requests, logging
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from rest_framework import exceptions, authentication
from functools import wraps

from django.contrib.auth.models import User
from call_centre.models import Operator
from cla_provider.models import Provider, Staff

OPERATOR_ROLE = "Civil Legal Advice Access"
OPERATOR_MANAGER_ROLE = "Civil Legal Advice Operator"
PROVIDER_ROLE = "Civil Legal Advice - Provider"


logger = logging.getLogger(__name__)

def logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise exceptions.AuthenticationFailed("Failed to validate user: %s" % str(e))
    return wrapper


class EntraAccessTokenAuthentication(authentication.BaseAuthentication):
    def __init__(self):
        self.tenant_id = settings.ENTRA_TENANT_ID
        self.expected_audience = settings.ENTRA_EXPECTED_AUDIENCE
        self.issuer = "https://login.microsoftonline.com/%s/v2.0" % self.tenant_id
        self.discovery_url = "https://login.microsoftonline.com/%s/discovery/v2.0/keys" % self.tenant_id

    def authenticate_header(self, request):
        return 'Bearer realm="api"'

    @logging
    def _create_operator(self, payload, is_manager=False):
        user_email = payload.get("USER_EMAIL", None)
        if user_email is None:
           return None

        user = User(
            username= user_email,
            email=user_email,
            is_active=True,
            is_staff=False, # This will be overridden in call_centre.models.Operator.save
        )
        # We don't want this user to be able to log in using a username and password
        user.set_unusable_password()
        user.save()

        operator = Operator(
            user = user,
            is_manager= is_manager,
        )

        operator.save()
        return operator.user

    @logging
    def _create_provider(self, payload):
        user_email = payload.get("USER_EMAIL", None)
        firm_name = payload.get("FIRM_NAME",None)
        if not firm_name:
            return None

        provider = Provider.objects.active().get(name=firm_name)

        if not provider:
            return None

        user = User(
            username = user_email,
            email = user_email,
            is_staff=False,
            is_active=True,
        )
        # We don't want this user to be able to login using a username and password
        user.set_unusable_password()
        user.save()

        staff = Staff(
            user=user,
            provider=provider,
            is_manager=False
        )
        staff.save()

        return staff.user


    def _public_keys(self):

        keys = cache.get("entra_public_keys")
        if not keys:
            try:
                response = requests.get(self.discovery_url)
                response.raise_for_status()
                keys = response.json().get("keys", [])
                cache.set("entra_public_keys", keys, 86400)
            except Exception:
                raise exceptions.AuthenticationFailed("Failed to get the public key")

        return keys

    def _validate_token(self, token):
        try:
            return self.validate_token(token)
        except jwt.ExpiredSignatureError as e:
            raise exceptions.AuthenticationFailed("Token has expired: %s" % e)
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed("Invalid token format: %s" % e)
        except Exception as e:
            raise exceptions.AuthenticationFailed("Token validation failed: %s" % e)


    def validate_token(self, token):

        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        keys = self._public_keys()
        key_data = next((k for k in keys if k["kid"] == kid), None)

        if not key_data:
            cache.delete("entra_public_keys")
            keys = self._public_keys()
            key_data = next((k for k in keys if k["kid"] == kid), None)

        if not key_data:
            raise exceptions.AuthenticationFailed("Key ID not found")

        cert_str = "-----BEGIN CERTIFICATE-----\n%s\n-----END CERTIFICATE-----" % key_data["x5c"][0]
        cert_obj = load_pem_x509_certificate(cert_str.encode("utf-8"), default_backend())
        public_key = cert_obj.public_key()
        return jwt.decode(token, public_key, algorithms=["RS256"], audience=self.expected_audience, issuer=self.issuer)
    
    def get_or_create_user(self, payload):

        email = payload.get('USER_EMAIL', None)
        if not email:
            raise exceptions.AuthenticationFailed("Invalid Token format, email is missing from Token!")

        user = None
        try:
            user = authenticate(entra_id_email=email)
        except Exception:
            pass

        if user:
            return user

        user_roles = payload.get("APP_ROLES").decode('utf-8')
     
        if not user_roles:
            raise exceptions.AuthenticationFailed("Invalid token: missing required field APP_ROLES")

        is_manager = True if OPERATOR_MANAGER_ROLE in user_roles else False 

        if OPERATOR_ROLE in user_roles or OPERATOR_MANAGER_ROLE in user_roles:
            user = self._create_operator(payload, is_manager=is_manager)
            if not user:
                raise exceptions.AuthenticationFailed("Invalid token: Incorrect App role provided!")
            return user

        if PROVIDER_ROLE in user_roles:
            user = self._create_provider(payload)

            if not user:
                raise exceptions.AuthenticationFailed("Invalid token: Incorrect App role provided!")
            return user

        return None


    def authenticate(self, request):

        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return None

        # Make sure it's a JWT token and if not, exit the authenticate method
        if len(token.split(".")) != 3:
            return None

        # token will now be Bearer <token>, we are only interested in the token
        _, token = token.split(" ")
        if not token:
            return None

        payload = self._validate_token(token)
        user = self.get_or_create_user(payload)

        if not user:
            raise exceptions.AuthenticationFailed("Invalid token: Incorrect App role provided!")

        return user, payload


