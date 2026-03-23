import jwt
import time
import datetime
from mock import patch
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

from cla_auth.authentication import EntraAccessTokenAuthentication
from core.tests.mommy_utils import make_recipe
from django.core.urlresolvers import reverse
from cla_common.constants import REQUIRES_ACTION_BY

from cla_auth.constants import OPERATOR_ROLE, OPERATOR_MANAGER_ROLE, PROVIDER_ROLE, PROVIDER_MCC_ROLE

User = get_user_model()


class EntraTokenGeneratorMixin(object):
    def setUp(self):
        self.factory = RequestFactory()
        self.auth = EntraAccessTokenAuthentication()

        with self.settings(ENTRA_TENANT_ID="test-tenant-id", ENTRA_EXPECTED_AUDIENCE="test-audience"):
            self.auth = EntraAccessTokenAuthentication()

        self.tenant_id = "test-tenant-id"
        self.issuer = "https://login.microsoftonline.com/%s/v2.0" % self.tenant_id

        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        self.public_key = self.private_key.public_key()

        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Test"),
                x509.NameAttribute(NameOID.COMMON_NAME, u"test.com"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self.public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now())
            .not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))
            .sign(self.private_key, hashes.SHA256(), default_backend())
        )

        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
        cert_base64 = (
            cert_pem.replace("-----BEGIN CERTIFICATE-----\n", "")
            .replace("\n-----END CERTIFICATE-----\n", "")
            .replace("\n", "")
        )

        self.mock_jwks = {"keys": [{"kid": "test-kid-123", "x5c": [cert_base64], "kty": "RSA", "use": "sig"}]}
        self.test_user = self.create_user(email="test@example.com", username="test")

    def create_user(self, **kwargs):
        return User.objects.create(**kwargs)

    def _create_token(
        self,
        firm_name="THE FIRM NAME LTD",
        app_roles=OPERATOR_ROLE,
        expired=False,
        email="test@example.com",
        kid="test-kid-123",
    ):
        """Helper to create JWT tokens"""
        now = datetime.datetime.now()

        if expired:
            exp = now - datetime.timedelta(hours=1)
        else:
            exp = now + datetime.timedelta(hours=1)

        payload = {
            "iss": self.issuer,
            "aud": self.auth.expected_audience,
            "exp": exp,
            "iat": now,
            "preferred_username": email,
            "sub": "test-subject",
            "name": "Full Name",
            "APP_ROLES": app_roles,
            "FIRM_CODE": 00000,
            "FIRM_NAME": firm_name,
            "LAA_ACCOUNTS": 0000000,
            "USER_EMAIL": email,
        }

        token = jwt.encode(
            payload, self.private_key, algorithm="RS256", headers={"typ": "JWT", "alg": "RS256", "kid": kid}
        )

        return token


class EntraAccessTokenAuthenticationTest(EntraTokenGeneratorMixin, TestCase):

    @patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
    def test_valid_token_authentication(self, mock_public_keys):

        email = "testuser@mail.com"
        user = User(email=email, is_active=True)

        user.save()
        make_recipe("cla_provider.staff", user=user)

        mock_public_keys.return_value = self.mock_jwks["keys"]
        token = self._create_token(expired=False, email=email)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer %s" % token

        user, payload = self.auth.authenticate(request)
        exp = payload.get("exp")
        email = payload.get("preferred_username")

        self.assertGreater(exp, time.time())
        self.assertEqual(email, "testuser@mail.com")

    @patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
    def test_expired_token_authentication(self, mock_public_keys):
       
        mock_public_keys.return_value = self.mock_jwks["keys"]
        token = self._create_token(expired=True)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer %s" % token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    def test_no_token_returns_none(self):
      
        request = self.factory.get("/")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_token_missing_email_claim(self):
       
        now = datetime.datetime.now()
        payload = {
            "iss": self.issuer,
            "aud": self.auth.expected_audience,
            "exp": now + datetime.timedelta(hours=1),
            "iat": now,
            "sub": "test-subject",
            # No email claim
        }

        token = jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": "test-kid-123"})

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer %s" % token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    def test_invalid_signature(self):
        """Test authentication fails with invalid signature"""
        wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

        now = datetime.datetime.now()
        payload = {
            "iss": self.issuer,
            "aud": self.auth.expected_audience,
            "exp": now + datetime.timedelta(hours=1),
            "iat": now,
            "preferred_username": "test@example.com",
            "name": "John Doe [LAA]",
        }

        token = jwt.encode(payload, wrong_key, algorithm="RS256", headers={"kid": "test-kid-123"})

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer %s" % token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch("cla_auth.authentication.requests.get")
    @patch("cla_auth.authentication.cache")
    def test_public_keys_cached(self, mock_cache, mock_requests):
        """Test that public keys are cached"""
        mock_cache.get.return_value = None
        mock_requests.return_value.json.return_value = self.mock_jwks
        mock_requests.return_value.raise_for_status.return_value = None

        keys = self.auth._public_keys()

        mock_cache.set.assert_called_once_with("entra_public_keys", self.mock_jwks["keys"], 86400)
        self.assertEqual(keys, self.mock_jwks["keys"])

    @patch("cla_auth.authentication.requests.get")
    def test_public_keys_fetch_failure(self, mock_requests_get):
        """Test handling of public key fetch failure"""
        mock_requests_get.side_effect = Exception("Network error")

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
            self.auth._public_keys()

        self.assertIn("public key", str(context.exception).lower())

    @patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
    def test_user_exist_but_disable(self, mock_public_keys):
        """Test that authenticate returns None for a disabled user"""
        user = User(email="test1233@example.com", is_active=False)
        user.save()
        make_recipe("cla_provider.staff", user=user)

        mock_public_keys.return_value = self.mock_jwks["keys"]
        token = self._create_token(expired=False, email="test1233@example.com")

        response = self.client.get("/", HTTP_AUTHORIZATION="Bearer %s" % token)
        self.assertEqual(response.status_code, 404)

    @patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
    def test_create_operator_success(self, mock_public_keys):
        """Test successful creation of an operator manager"""
        mock_public_keys.return_value = self.mock_jwks["keys"]

        email = "provider@test.com"
        providers= [OPERATOR_ROLE, OPERATOR_MANAGER_ROLE]

        for operator in providers:
            token = self._create_token(firm_name="THE FIRM NAME LTD", app_roles=operator, email=email)

            request = self.factory.get("/")
            request.META["HTTP_AUTHORIZATION"] = "Bearer %s" % token

            user, _ = self.auth.authenticate(request)

            self.assertIsNotNone(user)
            self.assertEqual(user.email, email)


    
    @patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
    def test_create_operator_success(self, mock_public_keys):
        """Test successful creation of an operator manager"""
        mock_public_keys.return_value = self.mock_jwks["keys"]
        provider_name = "TEST FIRM 123A"
        provider = make_recipe("cla_provider.provider", name=provider_name, active=True)

        email = "provider@test.com"
        providers= [PROVIDER_ROLE, PROVIDER_MCC_ROLE]

        for provider in providers:
            token = self._create_token(firm_name=provider_name, app_roles=provider, email=email)

            request = self.factory.get("/")
            request.META["HTTP_AUTHORIZATION"] = "Bearer %s" % token

            user, _ = self.auth.authenticate(request)

            self.assertIsNotNone(user)
            self.assertEqual(user.email, email)



    @patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
    def test_create_provider_missing_firm_name(self, mock_public_keys):
        """Test provider creation fails when firm name is missing from token"""
        mock_public_keys.return_value = self.mock_jwks["keys"]

        now = datetime.datetime.now()
        payload = {
            "iss": self.issuer,
            "aud": self.auth.expected_audience,
            "exp": now + datetime.timedelta(hours=1),
            "iat": now,
            "USER_EMAIL": "nofirm@test.com",
            "APP_ROLES": PROVIDER_ROLE,
            # Missing FIRM_NAME
        }

        token = jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": "test-kid-123"})

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer %s" % token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)


    


class EntraAuthorizationTestCase(EntraTokenGeneratorMixin, TestCase):
    def setUp(self):
        super(EntraAuthorizationTestCase, self).setUp()

        self.settings_override = self.settings(
            ENTRA_TENANT_ID="test-tenant-id", ENTRA_EXPECTED_AUDIENCE="test-audience"
        )
        self.settings_override.enable()

        self.public_keys_patcher = patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
        self.public_keys_mock = self.public_keys_patcher.start()
        self.public_keys_mock.return_value = self.mock_jwks["keys"]

    def tearDown(self):
        self.public_keys_patcher.stop()

    def test_user_is_provider(self):
        """User is a provider and tries to access a case that belongs to them"""
        provider_name = "THE FIRM NAME LTD"
        provider = make_recipe("cla_provider.provider", name=provider_name, active=True)
        case = make_recipe(
            "legalaid.case",
            reference="AB-00-11-22",
            personal_details=make_recipe("legalaid.personal_details"),
            provider=provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
        )
        token = self._create_token(firm_name=provider_name, app_roles=PROVIDER_ROLE, email="test@localhost")
        url = reverse("cla_provider:case-detail", kwargs=dict(reference=case.reference))
        headers = {"HTTP_AUTHORIZATION": "Bearer %s" % token}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_user_is_provider_but_not_assigned_case(self):
        """The user is a provider but the case is not assigned to them"""
        user = User(email="test@localhost")
        user.save()
        staff_instance = make_recipe("cla_provider.staff", user=user)
        case = make_recipe(
            "legalaid.case",
            reference="AB-00-11-22",
            personal_details=make_recipe("legalaid.personal_details"),
            provider=make_recipe("cla_provider.provider"),
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
        )
        token = self._create_token(email=staff_instance.user.email)
        url = reverse("cla_provider:case-detail", kwargs=dict(reference=case.reference))
        headers = {"HTTP_AUTHORIZATION": "Bearer %s" % token}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 403)
