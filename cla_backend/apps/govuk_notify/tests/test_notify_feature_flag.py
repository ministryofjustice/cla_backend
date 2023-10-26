from cla_backend.apps.govuk_notify.api import GovUkNotify, NotifyEmailOrchestrator
from cla_backend import settings

class TestNotifyFeatureFlag:
    def test_feature_flag_enabled(self):
        settings.USE_EMAIL_ORCHESTRATOR_FLAG = True
        client = GovUkNotify()
        assert isinstance(client, NotifyEmailOrchestrator)
        assert not isinstance(client, GovUkNotify)

    def test_feature_flag_disabled(self):
        settings.USE_EMAIL_ORCHESTRATOR_FLAG = False
        client = GovUkNotify()
        assert isinstance(client, GovUkNotify)
        assert not isinstance(client, NotifyEmailOrchestrator)