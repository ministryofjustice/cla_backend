from cla_provider.models import Staff
from django.contrib.auth.hashers import check_password
from django_statsd.clients import statsd
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class LegacyCHSAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        in the HTTP Post authentication.  Otherwise returns `None`.
        """

        userid, password, org = \
            request.DATA.get('CHSUserName'), \
            request.DATA.get('CHSPassword'), \
            request.DATA.get('CHSOrganisationID')

        if not all([userid, password, org]):
            statsd.incr('provider_extract.malformed')
            return None

        try:
            staff = Staff.objects.get(chs_user=userid, chs_organisation=org)
        except (Staff.DoesNotExist, Staff.MultipleObjectsReturned):
            statsd.incr('provider_extract.auth_failed')
            raise AuthenticationFailed('Invalid username/password')


        user = staff.user
        if user is None or not user.is_active or not check_password(password, staff.chs_password):
            statsd.incr('provider_extract.auth_failed')
            raise AuthenticationFailed('Invalid username/password')

        return (user, None)

    def authenticate_header(self, request):
        return None
