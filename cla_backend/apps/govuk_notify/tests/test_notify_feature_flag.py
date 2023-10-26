from cla_backend.apps.govuk_notify.api import GovUkNotify, NotifyEmailOrchestrator
from django.test import TestCase, override_settings


class TestNotifyFeatureFlagEnabled(TestCase):

    @override_settings(USE_EMAIL_ORCHESTRATOR_FLAG=True)
    @override_settings(EMAIL_ORCHESTRATOR_URL="http://a-url.com")
    def test_feature_flag_enabled(self):
        client = GovUkNotify()
        assert isinstance(client, NotifyEmailOrchestrator)
        assert not isinstance(client, GovUkNotify)


class TestNotifyFeatureFlagDisabled(TestCase):

    @override_settings(USE_EMAIL_ORCHESTRATOR_FLAG=False)
    @override_settings(EMAIL_ORCHESTRATOR_URL="http://a-url.com")
    def test_feature_flag_disabled(self):
        client = GovUkNotify()
        assert isinstance(client, GovUkNotify)
        assert not isinstance(client, NotifyEmailOrchestrator)
