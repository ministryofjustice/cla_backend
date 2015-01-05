from rest_framework_httpsignature.authentication import SignatureAuthentication

from provider.oauth2.models import Client


class OBIEESignatureAuthentication(SignatureAuthentication):
    '''
    Authenticates via user's associated oauth client_id, signed using AWS-style
    HMAC-SHA256 HTTP signature, generated with oauth client_id and
    client_secret.

    This authentication class should only be used by the OBIEE data export
    API method.
    '''
    API_KEY_HEADER = 'X-Api-Key'

    def fetch_user_data(self, api_key):
        try:
            client = Client.objects.filter(client_id=api_key).first()
            return (client.user, client.client_secret)
        except Client.DoesNotExist:
            return None
