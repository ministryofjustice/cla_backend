from django import forms

from cla_common.constants import CASE_STATE_REJECTED, CASE_STATE_ACCEPTED, \
    CASE_STATE_CLOSED

from legalaid.forms import OutcomeForm


class RejectCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(RejectCaseForm, self).get_outcome_code_queryset()
        return qs.filter(case_state=CASE_STATE_REJECTED)

    def save(self, case, user):
        case.reject()

        super(RejectCaseForm, self).save(case, user)  # saves the outcome


class AcceptCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(AcceptCaseForm, self).get_outcome_code_queryset()
        return qs.filter(case_state=CASE_STATE_ACCEPTED)

    def save(self, case, user):
        case.accept()

        super(AcceptCaseForm, self).save(case, user)  # saves the outcome


class CloseCaseForm(OutcomeForm):
    def get_outcome_code_queryset(self):
        qs = super(CloseCaseForm, self).get_outcome_code_queryset()
        return qs.filter(case_state=CASE_STATE_CLOSED)

    def save(self, case, user):
        case.close()

        super(CloseCaseForm, self).save(case, user)  # saves the outcome
