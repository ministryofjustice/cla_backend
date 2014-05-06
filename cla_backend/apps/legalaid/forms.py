from django import forms

from legalaid.models import OutcomeCode, CaseOutcome


class OutcomeForm(forms.Form):
    outcome_code = forms.ModelChoiceField(
        queryset=OutcomeCode.objects, to_field_name='code', empty_label=None
    )
    outcome_notes = forms.CharField(required=False, max_length=500)

    def __init__(self, *args, **kwargs):
        super(OutcomeForm, self).__init__(*args, **kwargs)

        self.fields['outcome_code'].queryset = self.get_outcome_code_queryset()

    def get_outcome_code_queryset(self):
        return OutcomeCode.objects

    def save(self, case, user):
        data = self.cleaned_data

        CaseOutcome.objects.create(
            case=case, created_by=user,
            outcome_code=data['outcome_code'], notes=data['outcome_notes']
        )
