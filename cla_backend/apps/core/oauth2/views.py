from provider.oauth2.views import AccessTokenView as Oauth2AccessTokenView
from provider.views import OAuthError

from .forms import ClientIdPasswordGrantForm


class AccessTokenView(Oauth2AccessTokenView):
    def get_password_grant(self, request, data, client):
        form = ClientIdPasswordGrantForm(data, client=client)
        if not form.is_valid():
            raise OAuthError(form.errors)
        return form.cleaned_data
