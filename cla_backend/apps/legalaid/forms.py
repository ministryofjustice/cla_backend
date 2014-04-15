from django import forms

from legalaid.models import OutcomeCode, CaseOutcome


class OutcomeForm(forms.Form):
    outcome_code = forms.ModelChoiceField(queryset=OutcomeCode.objects, to_field_name='code')
    outcome_notes = forms.CharField(required=False, max_length=500)

    def save(self, case, user):
        data = self.cleaned_data

        CaseOutcome.objects.create(
            case=case, created_by=user,
            outcome_code=data['outcome_code'], notes=data['outcome_notes']
        )
