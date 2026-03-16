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
    
    
    def authenticate_user(self, email):
        try:
            user = authenticate(entra_id_email=email)
            return user
        except Exception:
            return None 

      
    @logging 
    def _create_operator(self, payload, manager=False):
        print("This is what suppose to be hitting")
        
        user_email = payload.get("USER_EMAIL", None)
        if user_email is None:
           return None

        user_instance = User(
            username= user_email, 
            email=user_email, 
            password="test",
            is_active=True,
            is_staff=True
        )
        user_instance.save()

        create_operator = Operator(
            user = user_instance, 
            organisation= None, 
            is_manager= manager, 
        )
    
        create_operator.save()
        return user_instance if user_instance else None

    @logging
    def _create_provider(self, payload):

        user_email = payload.get("USER_EMAIL", None)
        firm_name = payload.get("FIRM_NAME",None)

        if not firm_name:
            return None
       
        provider = Provider.objects.active().get(name=firm_name)
        if not provider:
            return None 
       
        user = self.authenticate_user(user_email)
        if user and user.email != user_email:

            user_instance = User(
                username= user_email, 
                email=user_email, 
                password="test",
                is_active=True,
                is_staff=True
                
            )
            user_instance.save()

        else:
            user_instance = user 

        if provider:

            create_staff = Staff(
                user = user_instance,
                provider = provider, 
                is_manager=False
            )
            create_staff.save()

        return user_instance if user_instance else None 
    

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
    

    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return None

        payload = self._validate_token(token)
        email = payload.get('USER_EMAIL', None)

        if not email:
            raise exceptions.AuthenticationFailed("Invalid Token format, email is missing from Token!")

        user = self.authenticate_user(email)

        if user and user.email == email:
            return user, payload

        user_role = payload.get("APP_ROLES")
        if not user_role:
            raise exceptions.AuthenticationFailed("Invalid token: missing required field APP_ROLES")

        # Handle roles
        ROLE_OPERATOR_MANAGER = "Civil Legaator Manager"
        ROLE_OPERATOR = "Civil Legal Advice Access"
        ROLE_PROVIDER = "Civil Legal Advice - Provider"

        if user_role in [ROLE_OPERATOR_MANAGER, ROLE_OPERATOR]:
            manager = False == ROLE_OPERATOR_MANAGER
            user = self._create_operator(payload, manager)
            
            if not user:
                raise exceptions.AuthenticationFailed("Invalid token: Incorrect App role provided!")
            return user, payload

        if user_role == ROLE_PROVIDER:
            user = self._create_provider(payload)
            
            if not user:
                raise exceptions.AuthenticationFailed("Invalid token: Incorrect App role provided!")
            return user, payload

        
        raise exceptions.AuthenticationFailed("Invalid token: Incorrect App role provided!")
