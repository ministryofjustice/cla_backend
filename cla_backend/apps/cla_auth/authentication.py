import jwt
import requests
import logging
import uuid
from django.db import transaction
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from rest_framework import exceptions, authentication
from django.core.validators import validate_email
from django.contrib.auth.models import User
from call_centre.models import Operator
from cla_provider.models import Provider, Staff

from cla_auth.constants import OPERATOR_ROLE, OPERATOR_MANAGER_ROLE, PROVIDER_ROLE, PROVIDER_MCC_ROLE

logger = logging.getLogger(__name__)


class EntraAccessTokenAuthentication(authentication.BaseAuthentication):
    def __init__(self):
        self.tenant_id = settings.ENTRA_TENANT_ID
        self.expected_audience = settings.ENTRA_EXPECTED_AUDIENCE
        self.issuer = "https://login.microsoftonline.com/%s/v2.0" % self.tenant_id
        self.discovery_url = "https://login.microsoftonline.com/%s/discovery/v2.0/keys" % self.tenant_id

    def authenticate_header(self, request):
        return 'Bearer realm="api"'

    def get_unique_username(self, payload):
        email = payload["USER_EMAIL"]
        validate_email(email)

        max_length = 30
        base = email.split("@")[0][:max_length].lower()

        if not User.objects.filter(username=base).exists():
            return base

        for counter in range(1, 100):
            suffix = str(counter)
            username = base[: max_length - len(suffix)] + suffix
            if not User.objects.filter(username=username).exists():
                return username

        return base[:20] + uuid.uuid4().hex[:7]

    def _create_operator(self, payload, is_manager=False):
        user_email = payload.get("USER_EMAIL")
        if not user_email:
            raise exceptions.AuthenticationFailed("Cannot create operator: USER_EMAIL missing from token payload")

        try:
            user_name = self.get_unique_username(payload)

            with transaction.atomic():
                user = User(
                    username=user_name,
                    email=user_email,
                    is_active=True,
                    is_staff=False,
                )
                user.set_unusable_password()
                user.save()

                operator = Operator(user=user, is_manager=is_manager)
                operator.save()

            return operator.user
        except Exception:
            return None

    def _create_provider(self, payload):
        user_email = payload.get("USER_EMAIL")
        firm_name = payload.get("FIRM_NAME")

        if not user_email or not firm_name:
            return None

        try:
            provider = Provider.objects.active().get(name=firm_name)
        except Exception:
            return None

        try:
            user_name = self.get_unique_username(payload)
            with transaction.atomic():
                user = User(
                    username=user_name,
                    email=user_email,
                    is_staff=False,
                    is_active=True,
                )
                user.set_unusable_password()
                user.save()

                staff = Staff(user=user, provider=provider, is_manager=False)
                staff.save()

            return staff.user

        except Exception:
            return None

    def _public_keys(self):
        keys = cache.get("entra_public_keys")
        if not keys:
            try:
                response = requests.get(self.discovery_url)
                response.raise_for_status()
                keys = response.json().get("keys", [])
                cache.set("entra_public_keys", keys, 86400)
            except Exception:
                raise exceptions.AuthenticationFailed("Failed to fetch public keys")

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
        return jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=self.expected_audience,
            issuer=self.issuer
        )

    def get_or_create_user(self, payload):
        email = payload.get("USER_EMAIL")
        if not email:
            logger.error("Token payload is missing USER_EMAIL", exc_info=True)
            raise exceptions.AuthenticationFailed("Token payload is missing USER_EMAIL")

        raw_roles = payload.get("APP_ROLES")
        if not raw_roles:
            logger.error("ENTRA: Token payload is missing APP_ROLES", exc_info=True)
            raise exceptions.AuthenticationFailed("Token payload is missing APP_ROLES")

        app_role = raw_roles if isinstance(raw_roles, list) else [raw_roles]

        try:
            user = authenticate(entra_id_email=email)
        except Exception:
            user = None

        if user:
            return app_role, user

        is_manager = True if OPERATOR_MANAGER_ROLE in app_role else False

        if OPERATOR_ROLE in app_role or OPERATOR_MANAGER_ROLE in app_role:
            user = self._create_operator(payload, is_manager=is_manager)
            return app_role, user

        if PROVIDER_ROLE in app_role or PROVIDER_MCC_ROLE in app_role:
            user = self._create_provider(payload)
            return app_role, user

        return app_role, None

    def authenticate(self, request, retried=False):
        token = request.META.get("HTTP_AUTHORIZATION")
        print("TOKEN", token)

        if not token:
            return None

        if len(token.split(".")) != 3:
            print("TOKEN FORMAT IS NOT VALID")
            logger.error("ENTRA: INVALID TOKEN FORMAT", exc_info=True)
            raise exceptions.AuthenticationFailed("INVALID TOKEN FORMAT")
            return None

        _, token = token.split(" ", 1)
        print("TOKEN WITHOUT BEARER", token)
        print("OTHERS", _)
        if not token:
            return None

        payload = self._validate_token(token)
        print("PAYLOAD", payload)
        app_role, user = self.get_or_create_user(payload)

        if not user:
            logger.error("ENTRA: Could not find or create user for token payload", exc_info=True)
            raise exceptions.AuthenticationFailed("Could not find or create user for token payload")

        self.sync_user_roles(user, app_role)
        return user, payload

    def sync_user_roles(self, user, silas_roles):
        if not hasattr(user, "operator"):
            return

        if OPERATOR_MANAGER_ROLE in silas_roles:  # User is operator manager in silas but operator in fox admin
            if not user.operator.is_manager:
                logger.info(
                    "ENTRA: User %s is an operator manager in silas but only operator in fox admin. promoting user to operator manager" % user.pk)
                user.operator.is_manager = True
                user.operator.save()
        elif user.operator.is_manager:  # User is operator  silas but is an operator manager in fox admin
            logger.info(
                "ENTRA: User %s is operator in silas but operator manager in fox admin. demoting user operator" % user.pk)
            user.operator.is_manager = False
            user.operator.save()
