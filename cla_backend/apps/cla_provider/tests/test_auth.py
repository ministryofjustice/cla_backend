from cla_provider.authentication import LegacyCHSAuthentication
from django.test import TestCase
from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from mock import MagicMock
from rest_framework.exceptions import AuthenticationFailed


class LegacyCHSAuthenticationTestCase(CLAProviderAuthBaseApiTestMixin, TestCase):

    def setUp(self):
        super(LegacyCHSAuthenticationTestCase, self).setUp()
        self.staff = self.user.staff

        self.staff.set_chs_password('password')
        self.staff.chs_organisation = 'org123'
        self.staff.chs_user = 'user'
        self.staff.save()


    def test_valid_login(self):
        authenticator = LegacyCHSAuthentication()
        mockRequest = MagicMock(DATA={'CHSOrganisationID': self.staff.chs_organisation,
                                      'CHSPassword': 'password',
                                      'CHSUserName': self.staff.chs_user
        })

        user, _ = authenticator.authenticate(mockRequest)
        self.assertIsNotNone(user)

    def test_valid_legacy_login(self):
        # CHSOrgansationID instead of CHSOrganisationID
        authenticator = LegacyCHSAuthentication()
        mockRequest = MagicMock(DATA={'CHSOrgansationID': self.staff.chs_organisation,
                                      'CHSPassword': 'password',
                                      'CHSUserName': self.staff.chs_user
        })

        user, _ = authenticator.authenticate(mockRequest)
        self.assertIsNotNone(user)

    def test_valid_login_but_is_active_false(self):
        self.user.is_active = False
        self.user.save()

        authenticator = LegacyCHSAuthentication()
        mockRequest = MagicMock(DATA={'CHSOrganisationID': self.staff.chs_organisation,
                                      'CHSPassword': 'password',
                                      'CHSUserName': self.staff.chs_user
        })

        with self.assertRaises(AuthenticationFailed):
            user, _ = authenticator.authenticate(mockRequest)

    def test_malformed_login(self):
        self.user.is_active = False
        self.user.save()

        authenticator = LegacyCHSAuthentication()
        mockRequest = MagicMock(DATA={'CCHSOrganisationID': self.staff.chs_organisation,
                                      'CCHSPassword': 'password',
                                      'CCHSUserName': self.staff.chs_user
        })

        self.assertIsNone(authenticator.authenticate(mockRequest))


    def test_bad_password(self):

        authenticator = LegacyCHSAuthentication()

        # bad pass
        mockRequest = MagicMock(DATA={'CHSOrganisationID': self.staff.chs_organisation,
                                      'CHSPassword': 'assword',
                                      'CHSUserName': self.staff.chs_user
        })

        with self.assertRaises(AuthenticationFailed):
            user, _ = authenticator.authenticate(mockRequest)

        # test bad org
        mockRequest = MagicMock(DATA={'CHSOrganisationID': self.staff.chs_organisation+'111',
                                      'CHSPassword': 'password',
                                      'CHSUserName': self.staff.chs_user
        })

        with self.assertRaises(AuthenticationFailed):
            user, _ = authenticator.authenticate(mockRequest)


        # test bad user
        mockRequest = MagicMock(DATA={'CHSOrganisationID': self.staff.chs_organisation,
                                      'CHSPassword': 'password',
                                      'CHSUserName': self.staff.chs_user+'qq'
        })

        with self.assertRaises(AuthenticationFailed):
            user, _ = authenticator.authenticate(mockRequest)

