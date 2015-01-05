import logging
import datetime

from django.conf import settings
from django.utils import timezone

from provider.oauth2.forms import PasswordGrantForm
from provider.forms import OAuthValidationError

from django_statsd.clients import statsd

from call_centre.models import Operator
from cla_provider.models import Staff

from .models import AccessAttempt


logger = logging.getLogger(__name__)


class ClientIdPasswordGrantForm(PasswordGrantForm):
    def __init__(self, *args, **kwargs):
        super(ClientIdPasswordGrantForm, self).__init__(*args, **kwargs)
        self.account_lockedout = False

    def get_user_model(self):
        # WARNING terrible! But working :-)
        ModelClazz = None
        if self.client:
            if self.client.name == 'operator':
                ModelClazz = Operator
            elif self.client.name == 'staff':
                ModelClazz = Staff
        return ModelClazz

    def clean_login_attempts(self):
        username = self.cleaned_data['username']

        cooloff_time = timezone.now() - datetime.timedelta(
            minutes=settings.LOGIN_FAILURE_COOLOFF_TIME
        )

        attempts = AccessAttempt.objects.filter(
            username=username,
            created__gt=cooloff_time
        ).count()

        if attempts >= settings.LOGIN_FAILURE_LIMIT:
            self.account_lockedout = True

            statsd.incr('account.lockout.created')
            logger.info('account locked out', extra={
                'username': username
            })

            raise OAuthValidationError({
                'error': "locked_out"
            })

    def on_form_invalid(self):
        if not self.account_lockedout:
            username = self.cleaned_data.get('username')
            if username:
                AccessAttempt.objects.create_for_username(username)

    def on_form_valid(self):
        username = self.cleaned_data.get('username')
        AccessAttempt.objects.delete_for_username(username)

    def clean(self):
        self.clean_login_attempts()

        ModelClazz = self.get_user_model()

        assert ModelClazz, u"Cannot identify client {name}".format(
            name=u'None' if not self.client else self.client.name
        )

        data = self.cleaned_data
        try:
            model = ModelClazz.objects.get(user__username=data.get('username'))
        except ModelClazz.DoesNotExist as e:
            raise OAuthValidationError({'error': 'invalid_grant'})

        if not model.user.is_active:
            raise OAuthValidationError({'error': 'account_disabled'})

        return super(ClientIdPasswordGrantForm, self).clean()
