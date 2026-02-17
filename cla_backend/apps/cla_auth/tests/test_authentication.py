import jwt
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
import datetime


from cla_auth.authentication import EntraAccessTokenAuthentication

User = get_user_model()


class EntraAccessTokenAuthenticationTest(TestCase):
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

        self.test_user = User.objects.create_user(username="testuser", email="test@example.com")

    def _create_token(self, expired=False, email="test@example.com", kid="test-kid-123"):
        """Helper to create JWT tokens"""
        now = datetime.datetime.now()

        if expired:
            exp = now - datetime.timedelta(hours=1)
        else:
            exp = now + datetime.timedelta(hours=1)

        payload = {
            "iss":  self.issuer,
            "aud": self.auth.expected_audience,
            "exp": exp,
            "iat": now,
            "preferred_username": email,
            "sub": "test-subject",
        }

        token = jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": kid})

        return token

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
        request.META["HTTP_BEARER"] = token

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
        request.META["HTTP_BEARER"] = token

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
            "iss": "https://sts.windows.net/%s/" % self.auth.tenant_id,
            "aud": self.auth.expected_audience,
            "exp": now + datetime.timedelta(hours=1),
            "iat": now,
            "sub": "test-subject"
            # No email claim
        }

        token = jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": "test-kid-123"})

        request = self.factory.get("/")
        request.META["HTTP_BEARER"] = token

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
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
        request.META["HTTP_BEARER"] = token

        with self.assertRaises(exceptions.AuthenticationFailed) as context:
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
            "aud": "579599585850909384846894988943",
            "iss": "https://sts.windows.net/%s/" % self.auth.tenant_id,
            "aud": self.auth.expected_audience,
            "exp": now + datetime.timedelta(hours=1),
            "iat": now,
            "preferred_username": "test@example.com",
            "name": "Jhon Doe [LAA]"
            
        }

        token = jwt.encode(payload, wrong_key, algorithm="RS256", headers={"kid": "test-kid-123"})

        request = self.factory.get("/")
        request.META["HTTP_BEARER"] = token

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
    def test_disabled_user_returns_with_warning(self, mock_authenticate, mock_requests_get, mock_cache):
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
        request.META["HTTP_BEARER"] = token

        user, _ = self.auth.authenticate(request)

        self.assertEqual(user, disabled_user)
        self.assertFalse(user.is_active)


        mock_authenticate.assert_called_once_with(entra_id_email="test@example.com")
    


    # def request_sucess_but_not_provider(self):
       
    #     now = datetime.datetime.now()
    #     payload = {
    #         "aud": "579599585850909384846894988943",
    #         "iss": "https://sts.windows.net/%s/" % self.auth.tenant_id,
    #         "aud": self.auth.expected_audience,
    #         "exp": now + datetime.timedelta(hours=1),
    #         "iat": now,
    #         "preferred_username": "test@example.com",
    #         "name": "Jhon Doe [LAA]"
            
    #     }

    #     token = jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": "test-kid-123"})



    # def request_sucess_valid_provider():
    #     pass 