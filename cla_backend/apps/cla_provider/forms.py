from cla_common.constants import CASELOGTYPE_ACTION_KEYS

from legalaid.forms import OutcomeForm


class RejectCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(RejectCaseForm, self).get_outcome_code_queryset()
        return qs.filter(action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_REJECT_CASE)

    def save(self, user):
        self.case.reject()

        super(RejectCaseForm, self).save(user)  # saves the outcome


class AcceptCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(AcceptCaseForm, self).get_outcome_code_queryset()
        return qs.filter(action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_ACCEPT_CASE)

    def save(self, user):
        self.case.accept()

        super(AcceptCaseForm, self).save(user)  # saves the outcome


class CloseCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(CloseCaseForm, self).get_outcome_code_queryset()
        return qs.filter(action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE)

    def save(self, user):
        self.case.close()

        super(CloseCaseForm, self).save(user)  # saves the outcome
