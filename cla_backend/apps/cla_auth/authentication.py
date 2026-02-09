import jwt
import requests
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from rest_framework import exceptions, authentication


class EntraAccessTokenAuthentication(authentication.BaseAuthentication):
    """
    Middleware for Django 1.8 to validate Entra ID OBO tokens.
    """

    def __init__(self):
        self.tenant_id = settings.ENTRA_TENANT_ID
        self.expected_audience = settings.ENTRA_EXPECTED_AUDIENCE
        self.discovery_url = "https://login.microsoftonline.com/%s/discovery/v2.0/keys" % self.tenant_id

    def authenticate_header(self, request):
        """
        Return a string that will be used as the value of the
        WWW-Authenticate header in a HTTP 401 response.
        """
        return 'Bearer realm="api"'

    def authenticate(self, request):
        token = request.META.get("HTTP_BEARER")
        try:
            payload = self.validate_token(token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token Expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid Token")
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid token - validation error")

        print("PAYLOAD", payload)
        if payload:
            # Use 'upn' or 'preferred_username' as the unique identifier
            email = payload.get("email")
            print("EMAIL", email)
            if email:
                # Authenticate using the custom backend we created earlier
                user = authenticate(entra_id_email=email)
                print("MIDDLEWARE USER", user)
                if user:
                    request.user = user
                    # Note: We don't call login(request, user) here because
                    # APIs usually stay stateless (don't create sessions).
                    return user, payload

        raise exceptions.AuthenticationFailed("Invalid token - could not authenticate")

    def get_public_keys(self):
        # Cache keys for 24 hours (Microsoft rotates them rarely)
        keys = cache.get("entra_public_keys")
        if not keys:
            res = requests.get(self.discovery_url)
            keys = res.json().get("keys")
            cache.set("entra_public_keys", keys, 86400)
        return keys

    def validate_token(self, token):
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        keys = self.get_public_keys()
        key_data = next((k for k in keys if k["kid"] == kid), None)

        if not key_data:
            return None

        # Parse the certificate
        cert_str = "-----BEGIN CERTIFICATE-----\n%s\n-----END CERTIFICATE-----" % key_data["x5c"][0]
        cert_obj = load_pem_x509_certificate(cert_str.encode("utf-8"), default_backend())
        public_key = cert_obj.public_key()

        # Verify signature and claims
        return jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=self.expected_audience,
            issuer="https://sts.windows.net/%s/" % self.tenant_id,
        )
