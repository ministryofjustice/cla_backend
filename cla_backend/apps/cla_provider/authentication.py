from django.contrib.auth.hashers import check_password
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from cla_provider.models import Staff


class LegacyCHSAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        in the HTTP Post authentication.  Otherwise returns `None`.
        """

        userid, password, org = (
            request.DATA.get("CHSUserName"),
            request.DATA.get("CHSPassword"),
            request.DATA.get("CHSOrganisationID", request.DATA.get("CHSOrgansationID")),
        )

        if not all([userid, password, org]):
            return None

        try:
            staff = Staff.objects.get(chs_user=userid, chs_organisation=org)
        except (Staff.DoesNotExist, Staff.MultipleObjectsReturned):
            raise AuthenticationFailed("Invalid username/password")

        user = staff.user
        if user is None or not user.is_active or not check_password(password, staff.chs_password):
            raise AuthenticationFailed("Invalid username/password")

        return user, None

    def authenticate_header(self, request):
        return None
