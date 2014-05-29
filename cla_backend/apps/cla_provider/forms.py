from django import forms

from cla_common.constants import CASE_STATES

from legalaid.forms import OutcomeForm


class RejectCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(RejectCaseForm, self).get_outcome_code_queryset()
        return qs.filter(case_state=CASE_STATES.REJECTED)

    def save(self, user):
        self.case.reject()

        super(RejectCaseForm, self).save(user)  # saves the outcome


class AcceptCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(AcceptCaseForm, self).get_outcome_code_queryset()
        return qs.filter(case_state=CASE_STATES.ACCEPTED)

    def save(self, user):
        self.case.accept()

        super(AcceptCaseForm, self).save(user)  # saves the outcome


class CloseCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(CloseCaseForm, self).get_outcome_code_queryset()
        return qs.filter(case_state=CASE_STATES.CLOSED)

    def save(self, user):
        self.case.close()

        super(CloseCaseForm, self).save(user)  # saves the outcome
