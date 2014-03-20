from provider.oauth2.forms import PasswordGrantForm
from provider.forms import OAuthValidationError

from call_centre.models import Operator
from cla_provider.models import Staff


class ClientIdPasswordGrantForm(PasswordGrantForm):
    def get_user_model(self):
        # TODO terrible! But working :-)
        ModelClazz = None
        if self.client:
            if self.client.name == 'operator':
                ModelClazz = Operator
            elif self.client.name == 'staff':
                ModelClazz = Staff
        return ModelClazz

    def clean(self):
        ModelClazz = self.get_user_model()

        assert ModelClazz, u"Cannot identify client {name}".format(
            name=u'None' if not self.client else self.client.name
        )

        data = self.cleaned_data
        try:
            ModelClazz.objects.get(user__username=data.get('username'))
        except ModelClazz.DoesNotExist as e:
            raise OAuthValidationError({'error': 'invalid_grant'})

        return super(ClientIdPasswordGrantForm, self).clean()
