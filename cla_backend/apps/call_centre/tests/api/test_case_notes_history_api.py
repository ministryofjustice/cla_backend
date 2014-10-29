from rest_framework.test import APITestCase

from legalaid.tests.views.test_base import CLAOperatorAuthBaseApiTestMixin
from legalaid.tests.views.mixins.case_notes_history_api import \
    CaseNotesHistoryAPIMixin


class CaseNotesHistoryViewSetTestCase(
    CLAOperatorAuthBaseApiTestMixin, CaseNotesHistoryAPIMixin, APITestCase
):
    pass
