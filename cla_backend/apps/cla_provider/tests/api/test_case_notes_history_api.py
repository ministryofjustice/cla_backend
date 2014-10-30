from rest_framework.test import APITestCase

from cla_common.constants import REQUIRES_ACTION_BY

from legalaid.tests.views.test_base import CLAProviderAuthBaseApiTestMixin
from legalaid.tests.views.mixins.case_notes_history_api import \
    CaseNotesHistoryAPIMixin


class CaseNotesHistoryViewSetTestCase(
    CLAProviderAuthBaseApiTestMixin, CaseNotesHistoryAPIMixin, APITestCase
):
    def make_parent_resource(self, **kwargs):
        kwargs.update({
            'provider': self.provider,
            'requires_action_by': REQUIRES_ACTION_BY.PROVIDER
        })
        return super(CaseNotesHistoryViewSetTestCase, self).make_parent_resource(
            **kwargs
        )

