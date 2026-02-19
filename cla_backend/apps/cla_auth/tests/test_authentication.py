import jwt
import json
import datetime
from mock import patch, Mock
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

User = get_user_model()


class EntraTokenGeneratorMixin(object):
    def setUp(self):
        """Set up test fixtures"""
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
        self.test_user = self.create_user(email="test@example.com")

    def create_user(self, **kwargs):
        return User.objects.create(**kwargs)

    def _create_token(self, expired=False, email="test@example.com", kid="test-kid-123"):
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
        }

        token = jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": kid})

        return token


class EntraAccessTokenAuthenticationTest(EntraTokenGeneratorMixin, TestCase):
    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    @patch("cla_auth.authentication.authenticate")
    def test_valid_token_authentication(self, mock_authenticate, mock_requests_get, mock_cache):
        """Test successful authentication with valid token"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        mock_authenticate.return_value = self.test_user

        token = self._create_token(expired=False)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token

        user, payload = self.auth.authenticate(request)
        email = payload.get("preferred_username")

        self.assertEqual(user, self.test_user)
        self.assertEqual(email, "test@example.com")
        mock_authenticate.assert_called_once_with(entra_id_email="test@example.com")

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    def test_expired_token_authentication(self, mock_requests_get, mock_cache):
        """Test authentication fails with expired token"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        token = self._create_token(expired=True)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    def test_no_token_returns_none(self):
        """Test that missing token returns None"""
        request = self.factory.get("/")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    def test_token_missing_email_claim(self, mock_requests_get, mock_cache):
        """Test authentication fails when token missing email claim"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        now = datetime.datetime.now()
        payload = {
            "iss": self.issuer,
            "aud": self.auth.expected_audience,
            "exp": now + datetime.timedelta(hours=1),
            "iat": now,
            "sub": "test-subject"
            # No email claim
        }

        token = jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": "test-kid-123"})

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    @patch("cla_auth.authentication.authenticate")
    def test_user_not_found(self, mock_authenticate, mock_requests_get, mock_cache):
        """Test authentication fails when user not found"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        mock_authenticate.return_value = None  # User not found

        token = self._create_token(expired=False)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    def test_invalid_signature(self, mock_requests_get, mock_cache):
        """Test authentication fails with invalid signature"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

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
        request.META["HTTP_AUTHORIZATION"] = token

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate(request)

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    def test_public_keys_cached(self, mock_requests_get, mock_cache):
        """Test that public keys are cached"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

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

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    @patch("cla_auth.authentication.authenticate")
    def test_user_exist_but_disable(self, mock_authenticate, mock_requests_get, mock_cache):
        """Test that a disabled user is returned with a warning flag in the payload"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        disabled_user = Mock()
        disabled_user.is_active = False
        mock_authenticate.return_value = disabled_user

        token = self._create_token(expired=False)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token

        user, _ = self.auth.authenticate(request)

        self.assertEqual(user, disabled_user)
        self.assertFalse(user.is_active)
        mock_authenticate.assert_called_once_with(entra_id_email="test@example.com")

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    @patch("cla_auth.authentication.authenticate")
    def test_request_success_but_not_provider(self, mock_authenticate, mock_get, mock_cache):
        """Test authentication succeeds but user is not an allowed provider"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        permission_denied_message = "You do not have permission to perform this action."
        mock_authenticate.side_effect = exceptions.AuthenticationFailed(permission_denied_message)

        token = self._create_token(expired=False)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token

        with self.assertRaises(exceptions.AuthenticationFailed) as ctx:
            self.auth.authenticate(request)

        self.assertEqual(str(ctx.exception.detail), permission_denied_message)

    @patch("cla_auth.authentication.cache")
    @patch("cla_auth.authentication.requests.get")
    @patch("cla_auth.authentication.authenticate")
    def test_request_success_valid_provider(self, mock_authenticate, mock_get, mock_cache):
        """Test authentication succeeds and returns empty list with 200 for valid provider"""

        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = self.mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_authenticate.return_value = self.test_user

        token = self._create_token(expired=False)

        request = self.factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token

        user, payload = self.auth.authenticate(request)

        self.assertEqual(user, self.test_user)
        self.assertEqual(payload.get("preferred_username"), "test@example.com")
        mock_authenticate.assert_called_once_with(entra_id_email="test@example.com")


class EntraAuthorizationTestCase(EntraTokenGeneratorMixin, TestCase):
    def setUp(self):
        super(EntraAuthorizationTestCase, self).setUp()

        # This will stay active for the duration of the test method
        self.settings_override = self.settings(
            ENTRA_TENANT_ID="test-tenant-id", ENTRA_EXPECTED_AUDIENCE="test-audience"
        )
        self.settings_override.enable()

        self.public_keys_patcher = patch("cla_auth.authentication.EntraAccessTokenAuthentication._public_keys")
        self.public_keys_mock = self.public_keys_patcher.start()
        self.public_keys_mock.return_value = self.mock_jwks["keys"]

    def tearDown(self):
        self.public_keys_patcher.stop()

    def test_user_is_not_provider(self):
        """User is NOT a provider and trys to access a case"""

        # Create a case assigned to a provider
        case = make_recipe(
            "legalaid.case",
            reference="AB-00-11-22",
            personal_details=make_recipe("legalaid.personal_details"),
            provider=make_recipe("cla_provider.provider"),
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
        )

        # Try to get the details of a case with a non-provider user using the provider API
        url = reverse("cla_provider:case-detail", kwargs=dict(reference=case.reference))
        token = self._create_token(email=self.test_user.email)
        headers = {"HTTP_AUTHORIZATION": token}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            json.loads(response.content), {"detail": "You do not have permission to perform this action."}
        )

    def test_user_is_provider(self):
        """User is a provider and trys to access a case that belongs to them"""

        # Create a case assigned to a provider
        user = make_recipe("cla_provider.staff", **dict(user__email="test@localhost"))
        case = make_recipe(
            "legalaid.case",
            reference="AB-00-11-22",
            personal_details=make_recipe("legalaid.personal_details"),
            provider=user.provider,
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
        )

        token = self._create_token(email=user.user.email)
        # Try to get the details of a case with a provider user using the provider API
        url = reverse("cla_provider:case-detail", kwargs=dict(reference=case.reference))
        headers = {"HTTP_AUTHORIZATION": token}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 200)

    def test_user_is_provider_but_not_assigned_case(self):
        """The user is a provider but the case is assigned to them."""

        user = make_recipe("cla_provider.staff", **dict(user__email="test@localhost"))
        case = make_recipe(
            "legalaid.case",
            reference="AB-00-11-22",
            personal_details=make_recipe("legalaid.personal_details"),
            provider=make_recipe("cla_provider.provider"),
            requires_action_by=REQUIRES_ACTION_BY.PROVIDER,
        )

        token = self._create_token(email=user.user.email)
        # Try to get the details of a case with a provider user using the provider API
        url = reverse("cla_provider:case-detail", kwargs=dict(reference=case.reference))
        headers = {"HTTP_AUTHORIZATION": token}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, 404)
