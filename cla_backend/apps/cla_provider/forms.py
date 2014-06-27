from cla_common.constants import CASELOGTYPE_ACTION_KEYS
from cla_eventlog.constants import LOG_ROLES
from cla_eventlog.registry import event_registry

from legalaid.forms import EventSpecificOutcomeForm


class RejectCaseForm(EventSpecificOutcomeForm):

    LOG_EVENT_KEY = 'reject_case'

    def save(self, user):
        self.case.reject()

        super(RejectCaseForm, self).save(user)  # saves the outcome


class AcceptCaseForm(EventSpecificOutcomeForm):

    LOG_EVENT_KEY = 'accept_case'

    def save(self, user):
        self.case.accept()

        super(AcceptCaseForm, self).save(user)  # saves the outcome


class CloseCaseForm(EventSpecificOutcomeForm):
    LOG_EVENT_KEY = 'close_case'

    def save(self, user):
        self.case.close()

        super(CloseCaseForm, self).save(user)  # saves the outcome
