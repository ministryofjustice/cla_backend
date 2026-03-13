import jwt,requests, logging
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from rest_framework import exceptions, authentication

from django.contrib.auth.models import User
from call_centre.models import Operator, Organisation
from cla_provider.models import Provider, Staff

logger = logging.getLogger(__name__)


"""
HGS HAVE OPERATORS - 
OPERATOR AND MANAGER 

LAW FIRM HAVE STAFF THAT COMES IN 
STAFF 
"""


class EntraAccessTokenAuthentication(authentication.BaseAuthentication):
    def __init__(self):
        self.tenant_id = settings.ENTRA_TENANT_ID
        self.expected_audience = settings.ENTRA_EXPECTED_AUDIENCE
        self.issuer = "https://login.microsoftonline.com/%s/v2.0" % self.tenant_id
        self.discovery_url = "https://login.microsoftonline.com/%s/discovery/v2.0/keys" % self.tenant_id

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
      

    def _create_operator(self, payload, manager):
        
        _user_email = payload.get("USER_EMAIL", None)
        _organisation = payload.get("FIRM_NAME", None)
    

        if _user_email is None:
           return None

        user_class = User(
            username= _user_email, 
            email=_user_email, 
            password="test", # passwords should be store as string
            is_active=True,
            is_staff=True
            
        )
        user_class.save()

        organisation_instance = Organisation(
            organisation=_organisation
        )

        create_operator = Operator(
            user = user_class, 
            organisation= organisation_instance, 
            is_manager= True, 
    
        )
    
        status = create_operator.save()

        return True if status else False 


    def _create_provider(self, payload):

        _user_email = payload.get("USER_EMAIL", None)
        NAME = payload.get("FIRM_NAME", None),
        LAW_CATEGORY= payload.get("LAA_ACCOUNTS", None)
        ACTIVE=True
      

        if _user_email or NAME  is None:
            return None

        provider = Provider (
            name= NAME,
            opening_hours=None, 
            law_category = LAW_CATEGORY,
            active=ACTIVE,
            short_code =None,
            telephone_frontdoor= None, 
            telephone_backdoor=None,
            email_address =None
        )

        provider.save()
        # create user instance
        user_class = User(
            username=_user_email, 
            email=_user_email, 
            password=None,
            is_active=True
        )
    
        if provider:

            create_provider = Staff(
                user = user_class,
                provider = provider, 
                is_manager=False
            )

            create_provider.save()

            return True if create_provider else False
        
        return False

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
        

    def authenticate(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
    
        if not token:
            return None

        payload = self._validate_token(token)
 
        email = payload.get('preferred_username', None)
        if not email:
            raise exceptions.AuthenticationFailed("Invalid Token format")

        try:
            user = authenticate(entra_id_email=email)
            logger.info("User %s authenticated with entra token", str(user.get_username()))
            return user, payload
        
        except Exception:
            user_role = payload.get("APP_ROLES", None)
            if not user_role:
                raise exceptions.AuthenticationFailed(
                    "Invalid token: missing required field APP_ROLES"
                )
            
            
            # HGS EMPLOYEES (OPERATOR/OPERATOR MANAGER)
            ROLE_OPERATOR_MANAGER = "Civil Legal Advice Operator Manager"
            ROLE_OPERATOR = "Civil Legal Advice Access"

            # LAW FIRM STAFF 
            ROLE_PROVIDER = "Civil Legal Advice - Provider"

            if user_role == ROLE_OPERATOR_MANAGER or user_role == ROLE_OPERATOR:

                manager = True if ROLE_OPERATOR_MANAGER else False
        
                _user = self._create_operator(payload, manager)
                
                if not _user:
                    raise exceptions.AuthenticationFailed(
                    "Invalid token: Incorrect App role provided!"
                )

                return _user, payload

            elif user_role == ROLE_PROVIDER:
                _user =  self._create_operator_manager(payload)
               
                if not _user:
                   raise exceptions.AuthenticationFailed(
                    "Invalid token: Incorrect App role provided!"
                )
                
                return _user, payload
                
            else:
                raise exceptions.AuthenticationFailed(
                    "Invalid token: Incorrect App role provided!"
                )



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
