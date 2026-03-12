import jwt,requests, logging
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from rest_framework import exceptions, authentication

from call_centre.models import Operator
from cla_provider.models import Provider, Staff

logger = logging.getLogger(__name__)


class EntraAccessTokenAuthentication(authentication.BaseAuthentication):
    def __init__(self):
        self.tenant_id = settings.ENTRA_TENANT_ID
        self.expected_audience = settings.ENTRA_EXPECTED_AUDIENCE
        self.issuer = "https://login.microsoftonline.com/%s/v2.0" % self.tenant_id
        self.discovery_url = "https://login.microsoftonline.com/%s/discovery/v2.0/keys" % self.tenant_id

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
    
    def _decode(self,value):
        if value:    
            value.encode('utf-8')
            return value.decode('utf-8')
        
        return value
    

    def _create_operator(self, payload):

        user = payload.get("USER_EMAIL", None).encode('utf-8')
        organisation = str(payload.get("FIRM_NAME", ""))
        is_manager = payload.get("is_manager", False)
        is_cla_superuser = payload.get("is_cla_superuser", False)

        if user is None:
            return None


        create_operator = Operator(
            user = user, 
            organisation= organisation, 
            is_manager= is_manager, 
            is_cla_superuser= is_cla_superuser
        )

        status = create_operator.save()


        return True if status else False 


    def _create_operator_manager(self, payload):
        
        user = payload.get("user", None)
        organisation = payload.get("organisation", None)
        is_manager = payload.get("is_manager", None)
        is_cla_superuser = payload.get("is_cla_superuser", None)

       

        if user is None:
           return None

        if is_manager is None:
            is_manager = False

        if is_cla_superuser is None:
            is_cla_superuser = False

        create_operator = Operator(
            user = user, 
            organisation= organisation, 
            is_manager= is_manager, 
            is_cla_superuser= is_cla_superuser
        )

        status = create_operator.save()

        return True if status else False 


    def _create_provider(self, payload):

        USER = payload.get("USER_EMAIL", None)
        NAME = payload.get("FIRM_NAME", None),
        LAW_CATEGORY= payload.get("LAA_ACCOUNTS", None)
        ACTIVE=True
        SHORT_CODE = payload.get("FIRM_CODE", None)

        if USER or NAME or LAW_CATEGORY or SHORT_CODE is None:
            return None

        provider = Provider (
            name= NAME,
            opening_hours=None, 
            law_category = LAW_CATEGORY,
            active=ACTIVE,
            short_code =SHORT_CODE,
            telephone_frontdoor= None, 
            telephone_backdoor=None,
            email_address =None
        )

        if provider:

            create_provider = Staff(
                user = USER,
                provider = provider, 
                is_manager=False
            )

            return True if create_provider else False


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
 
        email = payload.get('preferred_username')
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

            ROLE_OPERATOR_MANAGER = "Civil Legal Advice Operator Manager"
            ROLE_OPERATOR = "Civil Legal Advice Access"
            ROLE_PROVIDER = "Civil Legal Advice - Provider"

            if user_role == ROLE_OPERATOR_MANAGER:
                _user = self._create_operator_manager(payload)
                raise exceptions.AuthenticationFailed(
                    "Invalid token: Incorrect App role provided!"
                )
               
            elif user_role == ROLE_OPERATOR:
                _user =  self._create_operator(payload)

                if not _user:
                
                    raise exceptions.AuthenticationFailed(
                        "Invalid token: Incorrect App role provided!"
                    ) 
                
            elif user_role == ROLE_PROVIDER:
               _user =  self._create_operator_manager(payload)
               
               if not _user:
                   raise exceptions.AuthenticationFailed(
                    "Invalid token: Incorrect App role provided!"
                )
                
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
